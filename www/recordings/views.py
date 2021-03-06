import datetime
import wave
import os
import urllib
from tempfile import TemporaryFile
from collections import Counter
import math
import mimetypes
import random
import json
import urllib

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect, Http404
from wsgiref.util import FileWrapper
from django.conf import settings
from django.db.models import Sum, Count
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import utc

from www.recordings.models import (Snippet, Score, Detector, Tag, Analysis, 
    Deployment, Organisation, Identification, AnalysisSet, CallLabel, SonogramTransform,)

from .forms import TagForm
from .models import Recording, Site

import pytz

PER_PAGE = 100
FILTERS = {
    'score': {
        'score_maximum': 'score__lt',
        'score_minimum': 'score__gt',
        'score': 'score',
        'snippet': 'snippet__id',
        'datetime_earliest': 'snippet__recording__datetime__gt',
        'datetime_latest': 'snippet__recording__datetime__lt',
        'sonogram_missing': 'snippet__sonogram__isnull',
        'site': 'snippet__recording__deployment__site__code',
        'recorder': 'snippet__recording__deployment__recorder',
        'owner': 'snippet__recording__deployment__owner__code',
    },
    'snippet': {
        'snippet': 'id',
        'datetime_earliest': 'recording__datetime__gt',
        'datetime_latest': 'recording__datetime__lt',
        'sonogram_missing': 'sonogram__isnull',
        'site': 'recording__deployment__site__code',
        'recorder': 'recording__deployment__recorder',
        'owner': 'recording__deployment__owner__code',
        'ids_lt': 'num_id__lt',
        'ids_gt': 'num_id__gt',
        'tag': 'sets__call_labels__tag__code',
        'tags_lt': 'num_tags__lt',
        'tags_gt': 'num_tags__gt',
        'labs_lt': 'num_labs__lt',
        'labs_gt': 'num_labs__gt',
    },
    'recording': {
        'recording': 'id',
        'datetime_earliest': 'datetime__gt',
        'datetime_latest': 'datetime__lt',
        'site': 'deployment__site__code',
        'recorder': 'deployment__recorder',
        'owner': 'deployment__owner__code',
    },
    'deployment': {
        'deployment': 'id',
        'datetime_earliest': 'end__gt',
        'datetime_latest': 'start__lt',
        'site': 'site__code',
        'recorder': 'recorder',
        'owner': 'owner__code',
    }
}


def _get_filters(request, level='snippet'):
    filters = {}
    fields = FILTERS[level]
    for key, field in fields.items():
        value = request.GET.get(key) or None
        if value:
            try:
                value = int(value)
            except:
                pass
            filters[field] = value
    return filters


def _get_order(request):
    return request.GET.getlist('order')

def _get_parameters(request):
    """Get the request parameters, apart from page and index"""
    parameters = request.GET.copy()
    while 'page' in parameters:
        del parameters['page']
    while 'index' in parameters:
        del parameters['index']
    return parameters.urlencode()

def home(request):
    duration = Recording.objects.all().aggregate(total_duration=Sum('duration'))
    duration = int(round(duration['total_duration']/(60*60*24), 0))
    return render(request, 'home.html', {'duration':duration, 'sites': Site.objects.count()})

def _get_snippet(id=None,
        organisation=None,
        site_code=None,
        date_time=None,
        offset=None,
        duration=None, 
        **kwargs):
    if organisation or\
            date_time or\
            site_code or\
            duration or\
            offset:
        return Snippet.objects.get(
                recording__datetime=datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc),
                recording__deployment__owner__code=organisation,
                recording__deployment__site__code=site_code,
                duration=duration,
                offset=offset,
            )
    else:
        return Snippet.objects.get(id=id)


def snippet(request, **kwargs):
    snippet = _get_snippet(**kwargs)
    analysis = kwargs.get('analysis', None)
    tags = Counter()
    if analysis and request.user:
        template = 'recordings/analysis_snippet.html'
        analysisset = AnalysisSet.objects.get(
            snippet__id=kwargs['id'],
            analysis=kwargs['analysis'])
        call_labels = CallLabel.objects.filter(analysisset=analysisset)
        identification, created = Identification.objects.get_or_create(
            analysisset=analysisset, 
            user=request.user)
        if created:
            identification.save()
            identification.tag_set = []
            identification.tag_set.add(*analysisset.analysis.tags.all())
            identification.save()
        id_before = not created
        tags.update(identification.tags.all())
    else:
        template = 'recordings/snippet.html'
        call_labels = CallLabel.objects.filter(analysisset__snippet=snippet)
        identifications = Identification.objects.filter(analysisset__snippet = snippet)
        tags = Counter()
        id_before = 0
        for i in identifications:
            tags.update(i.tags.all())
    count = kwargs.get('count', None)
    index =  kwargs.get('index', None)
    if index:
        count -= index
    count_all = kwargs.get('count_all', None)
    count_user = kwargs.get('count_user', None)
    favourite = snippet.fans.filter(id=request.user.id).count()
    favourites = snippet.fans.count()
    flagged = snippet.flags.count() > 0
    all_tags = Tag.objects.all().annotate(labels=Count('call_labels')).filter(labels__gt=0)
    for label in call_labels:
        #TODO: use the actual transform
        transform = list(SonogramTransform.objects.all())[-1]
        label.left, bottom = transform.physical_to_pixel(label.start_time, label.low_frequency)
        right, label.top = transform.physical_to_pixel(label.end_time, label.high_frequency)
        label.width = right - label.left
        label.height = bottom - label.top
    return render(request,
                  template,
                  {'snippet': snippet,
                   'all_tags': all_tags,
                   'datetime': snippet.datetime.astimezone(pytz.timezone(snippet.recording.deployment.start_timezone)),
                   'call_labels': call_labels,
                   'next_snippet': kwargs.get('next_snippet', None),
                   'previous_snippet': kwargs.get('previous_snippet', None),
                   'index': kwargs.get('index', None),
                   'next_index': kwargs.get('next_index', None),
                   'previous_index': kwargs.get('previous_index', None),
                   'random_index': kwargs.get('random_index', None),
                   'skip': kwargs.get('skip', None),
                   'count': count,
                   'flagged': flagged,
                   'count_all': count_all,
                   'count_user': count_user,
                   'favourite': favourite,
                   'favourites': favourites,
                   'analysis': analysis,
                   'id_before': id_before,
                   'tags': dict(tags)})

def _get_snippets(request, index):
    filters = _get_filters(request, level='snippet') or request.session.get('snippets_filters', {})
    for k, v in filters.items():
        if v == 'All':
            del filters[k]
    order = _get_order(request) or '-scores__score'
    request_parameters = _get_parameters(request)
    try:
        index = int(index)
    except ValueError:
        raise Http404 
    if index < 1:
        raise Http404 
    page = int(math.floor((index - 1)/PER_PAGE)) + 1
    # If we are still on the same page, return the next snippet
    if page == (int(math.floor((request.session.get('snippets_index', 0) - 1)/PER_PAGE)) + 1) and \
            order == request.session.get('snippets_order') and \
            filters == request.session.get('snippets_filters'):
        snippets = request.session.get('snippets_snippets', [])
        count = request.session.get('snippets_count', 0)
    # Otherwise, run a query to identify the next page
    else:
        code = 'simple-north-island-brown-kiwi'
        version = '0.1.2'
        detector = Detector.objects.get(code=code, version=version)
        snippet_ids = Snippet.objects.\
            filter(scores__detector = detector, scores__score__lt = 1e10).\
            filter(scores__detector = Detector.objects.get(code='amplitude'), scores__score__lt=32000).\
            order_by(order).\
            filter(**filters).\
            values_list('id', flat=True)
        paginator = Paginator(snippet_ids, PER_PAGE)
        # Handle return values outside the range
        if paginator.count == 0:
            return render(request, 'recordings/snippet.html', {})
        elif index > paginator.count or page > paginator.num_pages: 
            raise Http404
        snippet_page = paginator.page(page)
        snippets = list(snippet_page)
        count = paginator.count
        #Update the session
        request.session['snippets_snippets'] = snippets
        request.session['snippets_index'] = index
        request.session['snippets_order'] = order
        request.session['snippets_filters'] = filters
        request.session['snippets_count'] = count
    page_index = (index - 1) % PER_PAGE + 1
    if page_index > len(snippets):
        raise Http404
    # Now work out the next and previous  page and index
    next_index = index + 1 if index < count else None
    next_snippet = snippets[(next_index - 1) % PER_PAGE] if next_index else None
    previous_index = index - 1 if index > 1 else None
    previous_snippet = snippets[(previous_index - 1) % PER_PAGE] if previous_index else None
    
    return dict(id=snippets[page_index - 1],
        index=index,
        next_index=next_index,
        next_snippet=next_snippet,
        previous_index=previous_index,
        previous_snippet=previous_snippet,
        random_index=random.randint(0, count-1),
        count=count)

def snippets(request, index=1):
    return snippet(request, **_get_snippets(request, index))

def play_snippet(request, **kwargs):
    """Play a snippet. If we cant find it, generate it from the recording"""
    snippet = _get_snippet(**kwargs)
    filename = snippet.save_soundfile()
    return HttpResponseRedirect(reverse('snippet-media', args=(filename,))) 

def get_sonogram(request, **kwargs):
    """Get a sonogram. If we cant find it, generate it from the snippet"""
    snippet = _get_snippet(**kwargs)
    name = os.path.join(settings.SONOGRAM_DIR, snippet.get_sonogram_name())
    path = os.path.join(settings.MEDIA_ROOT, name)
    try:
        if not os.path.exists(path):
            raise ValueError
    except (ValueError, SuspiciousOperation, AttributeError):
        soundfile = snippet.save_soundfile()
        snippet.save_sonogram(replace=True)
    return HttpResponseRedirect(reverse('media', 
        args=(name,))) 

def get_sonogram_by_index(request, index):
    return get_sonogram(request, id=_get_snippets(request, index)['id'])

@login_required
def check_identification(request, analysisset):
    iden, created = Identification.objects.get_or_create(
        user=request.user, 
        analysisset=analysisset)
    if created:
        iden.save()
        iden.tag_set = []
        iden.tag_set.add(analysisset.analysis.tags.all())
        iden.save()
    label_tags = [label.tag for label in CallLabel.objects.filter(user=request.user, analysisset=analysisset)]
    iden_tags = list(iden.tags.all())
    for tag in iden.tag_set.all():
        if tag in label_tags and tag not in iden_tags:
            iden.tags.add(tag)
        elif tag not in label_tags and tag in iden_tags:
            iden.tags.remove(tag)
    iden.save()
    print iden.tags.all()

@login_required
@csrf_exempt
def api(request, id, action):
    print action, id, request.POST
    snippet = _get_snippet(id=id)
    result = dict(snippet=snippet.id, action=action)
    if action in ('favourite', 'unfavourite'):
        if action == 'favourite':
            snippet.fans.add(request.user)
        else:
            snippet.fans.remove(request.user)
        result['favourite'] = snippet.fans.filter(id=request.user.id).count()
        result['favourites'] = snippet.fans.count()
    elif action in ('flag', 'unflag'):
        if action == 'flag':
            snippet.flags.add(request.user)
        else:
            snippet.flags.remove(request.user)
        result['flag'] = int(snippet.flags.filter(id=request.user.id).count() > 0)
    elif action == 'call-label':
        labels = []
        for key in request.POST.keys():
            if key.startswith('call_label'):
                labels.append(request.POST.getlist(key))
        if labels:
            snippet = Snippet.objects.get(id=request.POST.get('snippet'))
            analysis = Analysis.objects.get(code=request.POST.get('analysis'))
            analysisset = AnalysisSet.objects.get(snippet=snippet, analysis=analysis)
            if SonogramTransform.objects.count() == 0:
                Snippet.objects.all()[0].save_sonogram(replace=True)
            transform = list(SonogramTransform.objects.all())[-1]
            for label in labels:
                start_time, low_frequency = transform.pixel_to_physical(float(label[2]), float(label[4]))
                end_time, high_frequency = transform.pixel_to_physical(float(label[3]), float(label[5]))
                call_label = CallLabel(
                    code=label[0],
                    user=request.user,
                    analysisset=analysisset,
                    tag=Tag.objects.get(code=label[1]),
                    start_time=start_time,
                    end_time=end_time,
                    low_frequency=low_frequency,
                    high_frequency=high_frequency)
                call_label.save()
                call_label.tag_set.add(*analysis.tags.all())
                call_label.save()
                check_identification(request, analysisset)
    elif action == 'call-label-delete':
        print request.POST
        call_label = CallLabel.objects.get(code=request.POST.get('call_label_id'))
        analysisset = call_label.analysisset
        call_label.delete()
        check_identification(request, analysisset)
    else:
       raise Http404 
    return HttpResponse(json.dumps(result), mimetype='application/json')


def tags(request):
    # TODO: Login required!
    tags = Tag.objects.all()
    if request.method == 'POST':  # If the form has been submitted...
        form = TagForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            form.save()
            return HttpResponseRedirect('/tags')  # Redirect after POST
    else:
        form = TagForm()  # An unbound form
    return render(request, 'recordings/tag_list.html', {'tags': tags, 'form': form})


def analysis_create(request):
    deployments = Deployment.objects.all()
    detectors = Detector.objects.all()
    tags = Tag.objects.all()
    organisations = Organisation.objects.all()
    if request.method == 'POST':
        POST = request.POST
        name = POST.get('name')
        description = POST.get('description')  if 'description' in POST else ''
        organisation = Organisation.objects.get(id__exact=POST.get('organisation'))
        analysis = Analysis(name=name,
                            description=description,
                            organisation=organisation)
        analysis.save()
        deployment_ids = POST.getlist('deployments')
        if 'all' in deployment_ids:
            deployment_ids = Deployment.objects.all().values_list('id', flat=True)
        analysis.deployments.add(*deployment_ids)
        analysis.tags.add(*POST.getlist('tags'))
        analysis.detectors.add(*POST.getlist('detectors'))
        if 'ubertag' in POST:
            analysis.ubertag = Tag.objects.get(id__exact=POST['ubertag'])
            analysis.save()
        return HttpResponseRedirect('/analysis')
    return render(request,
                  'recordings/analysis_create.html',
                  {'deployments': deployments,
                   'tags': tags,
                   'detectors': detectors,
                   'organisations': organisations})

def analysis_list(request):
    return render(request,
                  'recordings/analysis_list.html',
                  {'analyses': Analysis.objects.all()})


def analysis_detail(request, code):
    analysis = Analysis.objects.get(code=code)
    return render(request,
                  'recordings/analysis_detail.html',
                   {'analysis': analysis})


def _get_analysis_snippets(request, analysis, snippet_id, refresh=False):
    snippets = request.session.get('analysis_set', [])
    refresh = request.GET.get('refresh', '0') == '1' or refresh
    filters={'num_id__lt': 1}
    if not snippets or analysis.id != request.session.get('analysis_id', '') or refresh or request.session.get('analysis_filters', {}) != filters:
        user_snippets = Snippet.objects.filter(sets__analysis=analysis,
            sets__identifications__user=request.user)
        snippets = list(Snippet.objects.filter(sets__analysis=analysis).\
            annotate(num_id=Count('sets__identifications')).\
            annotate(num_tags=Count('sets__identifications__tags')).\
            annotate(num_labs=Count('sets__call_labels')).\
            filter(**filters).\
            order_by('?').\
            values_list('id', flat=True))
        request.session['analysis_set'] = snippets
        request.session['analysis_id'] = analysis.id
        request.session['analysis_filters'] = filters
    if snippet_id == 0:
        snippet_id = snippets[0]
    if not snippet_id in snippets:
        raise Http404
    try:
        Identification.objects.get(analysisset__snippet__id=snippet_id,
            analysisset__analysis=analysis, user=request.user)
        skip=request.session.get('analysis_skip', snippet_id)
    except Identification.DoesNotExist:
        skip=snippet_id
        request.session['analysis_skip'] = snippet_id
    index = snippets.index(snippet_id)
    next_index = index + 1 if index < len(snippets) - 1 else None
    previous_index = index - 1 if index > 0 else None
    next_snippet = snippets[next_index] if next_index else None
    previous_snippet = snippets[previous_index] if previous_index else None
    count_all = Snippet.objects.filter(sets__analysis=analysis).count()
    count_user = Snippet.objects.filter(sets__analysis=analysis,
            sets__identifications__user=request.user).count()
    return dict(id=snippet_id,
        index=index,
        analysis = analysis,
        next_snippet=next_snippet,
        previous_snippet=previous_snippet,
        skip = skip,
        count=len(snippets),
        count_user=count_user,
        count_all=count_all,
        )

@login_required
def analysis_snippet(request, code, snippet_id=0):
    analysis = Analysis.objects.get(code=code)
    if request.method == "POST":
        analysisset=AnalysisSet.objects.get(analysis=analysis,
            snippet=Snippet.objects.get(id=request.POST['snippet']))
        iden, created = Identification.objects.get_or_create(
                user=request.user, 
                analysisset=analysisset)
        iden.save()
        iden.tag_set = []
        iden.tag_set.add(*analysis.tags.all())
        tags = []
        for tag in analysis.tags.all():
            if request.POST[tag.code] == 'true':
                tags.append(tag)
        iden.tags = []
        if tags:
            iden.tags.add(*tags)
        iden.save()

        return redirect('analysis_snippet', code=code, snippet_id=request.POST["next_snippet"])
    analysis_snippets = _get_analysis_snippets(request, analysis, int(snippet_id), refresh=int(snippet_id)==0)
    if int(snippet_id) == 0:
        return redirect('analysis_snippet', code=code, snippet_id=analysis_snippets['id'])
    return snippet(request, **analysis_snippets)


@login_required
def analysis_next(request, code):
    this_analysis = Analysis.objects.get(code=code)
    return redirect('analysis_snippet', code=code, snippet_id=0)



def summary(request):

    # get the total duration
    duration = Recording.objects.all().aggregate(total_duration=Sum('duration'))
    duration = str(datetime.timedelta(seconds = round(duration['total_duration'], 0)))
    tags = Tag.objects.all().annotate(tag_count=Count('identifications')).order_by('-tag_count')

    return render(request,
                  'recordings/summary.html',
                  {
                    'recording_count': Recording.objects.count(),
                    'site_count': Site.objects.count(),
                    'deployment_count': Deployment.objects.count(),
                    'snippet_count': Snippet.objects.count(),
                    'duration': duration,
                    'identification_count': Identification.objects.count(),
                    'remaining_count': AnalysisSet.objects.filter(identifications__exact=None).count(),
                    'tags': tags
                  }
        )
