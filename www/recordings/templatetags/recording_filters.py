import os
import datetime
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def _snippet_url(snippet, url_name):
    return reverse(url_name,
        kwargs=dict(date_time = datetime.datetime.strftime(snippet.recording.datetime, "%Y%m%d%H%M%S"),
        recorder_code = snippet.recording.deployment.recorder.code,
        site_code = snippet.recording.deployment.site.code,
        organisation = snippet.recording.deployment.owner.code,
        offset = int(snippet.offset),
        duration = int(snippet.duration),)
    )
    
@register.filter
def wav_url(snippet):
    return _snippet_url(snippet, 'play_name')

@register.filter
def wav_name(snippet): 
    return os.path.split(_snippet_url(snippet, 'play_name'))[1]

@register.filter
def sonogram_url(snippet):
    return _snippet_url(snippet, 'sonogram')

@register.filter
def sonogram_name(snippet): 
    return os.path.split(_snippet_url(snippet, 'sonogram'))[1]

@register.filter
def snippet_name(snippet): 
    url = _snippet_url(snippet, 'snippet_name')
    if url.endswith('/'): 
        url = url[:-1]
    return os.path.split(url)[1]
