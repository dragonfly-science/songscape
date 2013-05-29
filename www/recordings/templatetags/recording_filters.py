import os
import datetime
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def _wav_url(snippet):
    return reverse('play_name',
        kwargs=dict(date_time = datetime.datetime.strftime(snippet.recording.datetime, "%Y%m%d%H%M%S"),
        recorder_code = snippet.recording.deployment.recorder.code,
        site_code = snippet.recording.deployment.site.code,
        organisation = snippet.recording.deployment.owner.code,
        offset = int(snippet.offset),
        duration = int(snippet.duration),)
    )
    
@register.filter
def wav_url(snippet):
    return _wav_url(snippet)

@register.filter
def wav_name(snippet): 
    return os.path.split(_wav_url(snippet))[0]
