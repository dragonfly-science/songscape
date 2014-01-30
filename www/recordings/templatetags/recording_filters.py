import os
import datetime
from django import template
from django.core.urlresolvers import reverse
from django.utils.timezone import utc

import pytz

register = template.Library()


timezone_lookup = dict([(pytz.timezone(x).localize(datetime.datetime.now()).tzname(), x) 
    for x in pytz.all_timezones])

def isotime(dt):
    """Returns a datetime in the ISO8601 UTC format"""
    return dt.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _snippet_url(snippet, url_name):
    return reverse(url_name,
        kwargs=dict(date_time = isotime(snippet.recording.datetime),
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
