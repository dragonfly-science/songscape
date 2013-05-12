import os
import datetime
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

#url(r'^play/(?P<organisation>[\w]+)-(?P<site_code>[\w]+)-(?P<datetime>\d+)-(?P<offset>[\d\.]+)-(?P<id>\d+).wav', 'www.recordings.views.play_snippet', name='play_name')
def _wav_url(snippet):
    return reverse('play_name',
        kwargs=dict(date_time = datetime.datetime.strftime(snippet.recording.datetime, "%Y%m%d%H%M%S"),
        recorder_code = snippet.recording.deployment.recorder.code,
        site_code = snippet.recording.deployment.site.code,
        organisation = snippet.recording.deployment.owner.code,
        offset = int(snippet.offset),
        id=snippet.id,)
    )
    
@register.filter
def wav_url(snippet):
    return _wav_url(snippet)

@register.filter
def wav_name(snippet): 
    return os.path.split(_wav_url(snippet))[0]
