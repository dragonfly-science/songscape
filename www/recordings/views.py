import wave
from recordings.models import Snippet, Score, Detector, Tag, Analysis
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect
from tempfile import TemporaryFile
from django.core.servers.basehttp import FileWrapper
from django.conf import settings

from .forms import TagForm

fields = (
    'score__lt',
    'score__gt',
    'score',
    'snippet__id',
    'snippet__recording__datetime__gt',
    'snippet__recording__datetime__lt',
    'snippet__sonogram__isnull',
    'snippet__recording__deployment__site__code',
    'snippet__recording__deployment__recorder',
    )
    
def _get_filters(request):
    filters = {}
    for field in fields:
        value = request.GET.get(field) or None
        if value:
            filters[field] = value
    return filters

def _get_order(request):
    return request.GET.getlist('order')

def _get_parameters(request):
    """Get the request parameters, apart from page"""
    parameters = request.GET.copy()
    while parameters.has_key('page'):
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

def snippet(request, id):
    snippets = request.session.get('snippets', [])
    if int(id) in snippets:
        index = snippets.index(int(id))
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
    snippet = Snippet.objects.get(id=id)
    return render(request, 'recordings/snippet.html', {'snippet':snippet, 'next_id':next_id, 'previous_id':previous_id})

def scores(request, code, version, default_page=1, per_page=500):
    filters = _get_filters(request)
    order = _get_order(request)
    request_parameters = _get_parameters(request)
    detector = Detector.objects.get(code=code, version=version)
    queryset = Score.objects.filter(detector=detector).select_related().filter(**filters).order_by(*order)
    request.session['snippets'] =  [score.snippet.id for score in queryset]
    scores = _paginate(request,
        queryset,
        default_page=default_page,
        per_page=per_page,
    )
    return render(request, 'recordings/scores_list.html', {'scores': scores, 'request_parameters': request_parameters})

def play_snippet(request, id):
    snippet = Snippet.objects.get(id=id)
    wav_file = TemporaryFile()
    wav_writer = wave.open(wav_file, 'wb')
    wav_writer.setframerate(snippet.recording.sample_rate)
    wav_writer.setsampwidth(2)
    wav_writer.setnchannels(snippet.recording.nchannels)
    wav_writer.writeframes(snippet.recording._get_frames(snippet.offset, snippet.duration))
    wav_writer.close()
    wav_length= wav_file.tell()
    wav_file.seek(0)
    response = StreamingHttpResponse(FileWrapper(wav_file), content_type='audio/wav')
    response['Content-Length'] = wav_length
    return response


def tags(request):
    tags = Tag.objects.all()
    if request.method == 'POST': # If the form has been submitted...
        form = TagForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            return HttpResponseRedirect('/tags') # Redirect after POST
    else:
        form = TagForm() # An unbound form
    return render(request, 'recordings/tag_list.html', {'tags': tags, 'form': form})
