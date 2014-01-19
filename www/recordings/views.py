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

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.db.models import Sum, Count
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt

from www.recordings.models import (Snippet, Score, Detector, Tag, Analysis, 
    Deployment, Organisation, Identification, AnalysisSet)

from .forms import TagForm
from .models import Recording, Site

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
    return render(request, 'home.html')

def _get_snippet(id=None,
        organisation=None,
        site_code=None,
        recorder_code=None,
        date_time=None,
        offset=None,
        duration=None, 
        **kwargs):
    if organisation or\
            date_time or\
            recorder_code or\
            site_code or\
            duration or\
            offset:
        return Snippet.objects.get(
                recording__datetime=datetime.datetime.strptime(date_time, "%Y%m%d%H%M%S"),
                recording__deployment__recorder__code=recorder_code,
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
    if analysis:
        template = 'recordings/analysis_snippet.html'
        identifications = Identification.objects.filter(
            analysisset__snippet_id__exact=kwargs['id'], 
            user_id__exact=request.user.id,
            analysisset__analysis=kwargs['analysis'])
        id_before = identifications.count() > 0
        tags = []
        if id_before:
            tags = identifications[0].tags.all()
    else:
        template = 'recordings/snippet.html'
        identifications = Identification.objects.filter(analysisset__snippet = snippet)
        tags = Counter()
        id_before = 0
        for i in identifications:
            tags.update(i.tags.all())
    count = kwargs.get('count', None)
    favourite = snippet.fans.filter(id=request.user.id).count()
    favourites = snippet.fans.count()
    return render(request,
                  template,
                  {'snippet': snippet,
                   'next_index': kwargs.get('next_index', None),
                   'previous_index': kwargs.get('previous_index', None),
                   'index': kwargs.get('index', None),
                   'count': count,
                   'favourite': favourite,
                   'favourites': favourites,
                   'analysis': analysis,
                   'id_before': id_before,
                   'tags': dict(tags)})

def _get_snippets(request, index):
    filters = _get_filters(request, level='snippet')
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
    if page == (int(math.floor((request.session.get('index', 0) - 1)/PER_PAGE)) + 1) and \
            order == request.session.get('order') and \
            filters == request.session.get('filters'):
        snippets = request.session.get('snippets', [])
        count = request.session.get('count', 0)
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
        request.session['snippets'] = snippets
        request.session['index'] = index
        request.session['order'] = order
        request.session['filters'] = filters
        request.session['count'] = count
    page_index = (index - 1)%PER_PAGE + 1
    if page_index > len(snippets):
        raise Http404
    # Now work out the next and previous  page and index
    next_index = index + 1
    previous_index = index - 1
    if previous_index < 1:
        previous_index = None
    if next_index > count:
        next_index = None
    return dict(id=snippets[page_index - 1],
        index=index,
        next_index=next_index,
        previous_index=previous_index,
        count=count)

def snippets(request, index=1):
    return snippet(request, **_get_snippets(request, index))

def _guarantee_soundfile(snippet):
    try:
        if not os.path.exists(snippet.soundfile.path):
            raise ValueError
    except (ValueError, SuspiciousOperation, AttributeError):
        snippet.save_soundfile(replace=True)
    if snippet.soundfile and not snippet.soundfile.name.startswith(settings.SNIPPET_DIR):
        snippet.soundfile.name = os.path.join(settings.SNIPPET_DIR, snippet.get_soundfile_name())
        snippet.save()

def play_snippet(request, **kwargs):
    """Play a snippet. If we cant find it, generate it from the recording"""
    snippet = _get_snippet(**kwargs)
    _guarantee_soundfile(snippet)
    return HttpResponseRedirect(reverse('media', args=(snippet.soundfile.name,))) 

def get_sonogram(request, **kwargs):
    """Get a sonogram. If we cant find it, generate it from the snippet"""
    snippet = _get_snippet(**kwargs)
    _guarantee_soundfile(snippet)
    try:
        if not os.path.exists(snippet.sonogram.path):
            raise ValueError
    except (ValueError, SuspiciousOperation, AttributeError):
        snippet.save_sonogram(replace=True)
    if snippet.sonogram and not snippet.sonogram.name.startswith(settings.SONOGRAM_DIR): #name should not be absolute
        snippet.sonogram.name = os.path.join(settings.SONOGRAM_DIR, snippet.get_sonogram_name())
        snippet.save()
    return HttpResponseRedirect(reverse('media', 
        args=(snippet.sonogram.name,))) 

def get_sonogram_by_index(request, index):
    return get_sonogram(request, id=_get_snippets(request, index)['id'])

@login_required
@csrf_exempt
def api(request, id, action):
    snippet = _get_snippet(id=id)
    result = dict(snippet=snippet.id, action=action)
    if action in ('favourite', 'unfavourite'):
        if action == 'favourite':
            snippet.fans.add(request.user)
        else:
            snippet.fans.remove(request.user)
        result['favourite'] = snippet.fans.filter(id=request.user.id).count()
        result['favourites'] = snippet.fans.count()
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


def _get_analysis_snippets(request, analysis, index):
    snippets = request.session.get('analysis_set', [])
    if not snippets or analysis.id != request.session.get('analysis_id', ''):
        snippets = [a.snippet.id for a in
            AnalysisSet.objects.filter(analysis=analysis).order_by('?')]
        request.session['analysis_set'] = snippets
        request.session['analysis_id'] = analysis.id
    if index < 0 or index >= len(snippets):
        raise Http404
    if index:
        next_index = index + 1 if index < len(snippets) - 1 else None
        previous_index = index - 1 if index > 0 else None
    else:
        next_index = 1
        previous_index = None
    return dict(id=snippets[index],
        index=index,
        analysis = analysis,
        next_index=next_index,
        previous_index=previous_index,
        count=len(snippets))

@login_required
def analysis_snippet(request, code, index=0):
    analysis = Analysis.objects.get(code=code)
    if request.method == "POST":
        iden = Identification(user=request.user, 
            analysisset=AnalysisSet.objects.get(analysis=analysis,
                    snippet=Snippet.objects.get(id=request.POST['snippet'])
                ),
            comment="")
        iden.save()
        iden.tag_set.add(*analysis.tags.all())
        tags = []
        for tag in analysis.tags.all():
            if request.POST[tag.code] == 'true':
                tags.append(tag)
        if tags:
            iden.tags.add(*tags)
        iden.save()

        return redirect('analysis_snippet', code=code, index=request.POST["next_index"])
    return snippet(request, **_get_analysis_snippets(request, analysis, int(index)))

def analysis(request, code):
    this_analysis = Analysis.objects.get(code=code)
    tag_summary = {}
    for tag in this_analysis.tags.all():
        tag_summary[tag.name] = tag.identifications.filter(analysis=this_analysis).count()
    sort_options = ['score', 'time', 'random']

    identifications = Identification.objects.filter(analysisset__analysis=this_analysis).select_related()
    identification_list = [(x.snippet, x.snippet.recording.deployment.site.code,
        datetime.datetime.strftime(x.snippet.datetime, "%Y-%m-%d"),
        datetime.datetime.strftime(x.snippet.datetime, "%H:%M:%S"),
        ";".join([t.code for t in x.tags.all()]),
        "%0.1s%0.1s"%(x.user.first_name, x.user.last_name)) for x in
                           identifications]

    return render(request,
            'recordings/analysis.html',
            {'sort_options': sort_options,
                'analysis': this_analysis,
                'tag_summary': tag_summary,
            }
        )


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
                    'remaining_count': Snippet.objects.filter(identifications__exact=None).count(),
                    'tags': tags
                  }
        )
