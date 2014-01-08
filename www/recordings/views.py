import datetime
import wave
import os
import urllib
from tempfile import TemporaryFile
from collections import Counter
import mimetypes

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.db.models import Sum, Count
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation


from www.recordings.models import (Snippet, Score, Detector, Tag, Analysis, 
    Deployment, Organisation, Identification, AnalysisSet)

from .forms import TagForm
from .models import Recording, Site

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


def _get_filters(request, level='score'):
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
    """Get the request parameters, apart from page"""
    parameters = request.GET.copy()
    while 'page' in parameters:
        del parameters['page']
    return parameters.urlencode()


def _paginate(request, queryset, per_page=500, default_page=1):
    page = request.GET.get('page') or default_page
    paginator = Paginator(queryset, per_page)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    return results


def _get_snippets(request, per_page, page=1, **filters):
    page = request.GET.get('page') or page
    for field in fields:
        value = request.GET.get(field) or None
        if value:
            filters[field] = value
    snippets_list = Snippet.objects.select_related().filter(**filters)
    paginator = Paginator(snippets_list, per_page)
    try:
        snippets = paginator.page(page)
    except PageNotAnInteger:
        snippets = paginator.page(1)
    except EmptyPage:
        snippets = paginator.page(paginator.num_pages)
    return snippets

def home(request):
    return render(request, 'home.html')

def _get_snippet(id=None,
        organisation=None,
        site_code=None,
        recorder_code=None,
        date_time=None,
        offset=None,
        duration=None):
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
    snippets = request.session.get('snippets', [])
    if snippet.id in snippets:
        index = snippets.index(snippet.id)
        try:
            next_id = snippets[index + 1]
        except IndexError:
            next_id = None
        try:
            previous_id = snippets[index - 1]
        except IndexError:
            previous_id = None
    else:
        next_id = None
        previous_id = None

    idens = snippet.identifications.all()
    tags = Counter()
    for iden in idens:
        tags.update(iden.true_tags.all())

    return render(request,
                  'recordings/snippet.html',
                  {'snippet': snippet,
                   'next_id': next_id,
                   'previous_id': previous_id,
                   'tags': dict(tags)})


def snippets(request, default_page=1, per_page=100):
    filters = _get_filters(request, level='score')
    order = _get_order(request)
    if len(order) == 0:
        order = ['-score']
    request_parameters = _get_parameters(request)
    code = 'simple-north-island-brown-kiwi'
    version = '0.1.2'
    clipping = Detector.objects.get(code='amplitude')
    unclipped_scores = Score.objects.filter(detector=clipping, score__lt=32000)
    unclipped_snippets = Snippet.objects.filter(scores__in=unclipped_scores)
    detector = Detector.objects.get(code=code, version=version)
    queryset = Score.objects.filter(
        detector=detector, snippet__in=unclipped_snippets).select_related().filter(**filters).order_by(*order)
    scores = _paginate(request,
                       queryset,
                       default_page=default_page,
                       per_page=per_page,
                       )
    # It takes over 30 seconds to extract the id for 130k snippets/scores!
    # So for now just extract the snippet id for the current page.
    # TODO: put the ordering in a method and repopulate it if the user
    # gets to the edge...
    request.session['snippets'] = [score.snippet.id for score in scores]
    return render(request, 'recordings/snippets_list.html', {'scores': scores, 'request_parameters': request_parameters})


def play_snippet(request, **kwargs):
    """Play a snippet. If we cant find it, generate it from the recording"""
    snippet = _get_snippet(**kwargs)
    try:
        if not os.path.exists(snippet.soundfile.path):
            raise ValueError
    except (ValueError, SuspiciousOperation, AttributeError):
        snippet.save_soundfile(replace=True)
    if snippet.soundfile and not snippet.soundfile.name.startswith(settings.SNIPPET_DIR): #name should not be absolute
        snippet.soundfile.name = os.path.join(settings.SNIPPET_DIR, snippet.get_soundfile_name())
        snippet.save()
    return HttpResponseRedirect(os.path.join(settings.MEDIA_URL, snippet.soundfile.name)) 

def get_sonogram(request, **kwargs):
    """Play a snippet. If we cant find it, generate it from the snippet"""
    snippet = _get_snippet(**kwargs)
    try:
        if not os.path.exists(snippet.sonogram.path):
            raise ValueError
    except (ValueError, SuspiciousOperation, AttributeError):
        snippet.save_sonogram(replace=True)
    if snippet.sonogram and not snippet.sonogram.name.startswith(settings.SONOGRAM_DIR): #name should not be absolute
        snippet.sonogram.name = os.path.join(settings.SONOGRAM_DIR, snippet.get_sonogram_name())
        snippet.save()
    return HttpResponseRedirect(os.path.join(settings.MEDIA_URL, snippet.sonogram.name)) 

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


@login_required
def analysis_snippet(request, code, snippet_id=None):
    snippet = Snippet.objects.get(id=snippet_id)
    analysis = Analysis.objects.get(code=code)
    if request.method == "POST":
        true_tags = []
        false_tags = []
        for tag in analysis.tags.all():
            if request.POST[tag.code] == 'true':
                true_tags.append(tag)
            else:
                false_tags.append(tag)

        iden = Identification(user = request.user, analysis=analysis, snippet=snippet, comment="")
        iden.save()
        iden.true_tags.add(*true_tags)
        iden.false_tags.add(*false_tags)

        return redirect('analysis_snippet', code=code, snippet_id=request.POST["next_id"])

    snippets = request.session.get('analysis_set', [])
    if not snippets:
        snippets = [a.snippet.id for a in AnalysisSet.objects.filter(analysis=analysis).order_by('?')]
        request.session['analysis_set'] = snippets
    previous = Identification.objects.filter(analysis=analysis)
    if snippet_id and int(snippet_id) in snippets:
        index = snippets.index(int(snippet_id))
        try:
            next_id = snippets[index + 1]
        except IndexError:
            next_id = None
        try:
            previous_id = snippets[index - 1]
        except IndexError:
            previous_id = None
    else:
        index = 0
        snippet_id = snippets[0]
        next_id = snippets[1]
        previous_id = None

    previous_identification = Identification.objects.filter(snippet_id__exact=snippet_id, user_id__exact=request.user.id)

    id_before = previous_identification.count() > 0
    true_tags = []
    false_tags = []
    if id_before:
        true_tags = previous_identification[0].true_tags.all()
        false_tags = previous_identification[0].false_tags.all()


    return render(request,
                  'recordings/analysis_snippet.html',
                  {'snippet': snippet,
                   'analysis': analysis,
                   'next_id': next_id,
                   'id_before': id_before,
                   'true_tags': true_tags,
                   'false_tags': false_tags,
                   'previous_id': previous_id,
                   'index': index,
                   'n_snippets': len(snippets)})


def analysis(request, code):
    this_analysis = Analysis.objects.get(code=code)
    tag_summary = {}
    for tag in this_analysis.tags.all():
        tag_summary[tag.name] = tag.identifications.filter(analysis=this_analysis).count()
    sort_options = ['score', 'time', 'random']

    identifications = Identification.objects.filter(analysis=this_analysis).select_related()
    identification_list = [(x.snippet, x.snippet.recording.deployment.site.code,
        datetime.datetime.strftime(x.snippet.datetime, "%Y-%m-%d"),
        datetime.datetime.strftime(x.snippet.datetime, "%H:%M:%S"),
        ";".join([t.code for t in x.true_tags.all()]),
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
