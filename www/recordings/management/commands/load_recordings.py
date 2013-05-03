from datetime import datetime
import os
from time import time, strptime, mktime
import wave
import contextlib

from django.core.management.base import BaseCommand
from django.conf import settings

from recordings.models import Deployment, Recording, Snippet


def get_starttime(filename, count=0):
    """returns the start time, by parsing the filename of a WAV file from the DOC recorders"""
    timestamp = mktime(strptime(filename, "%d%m%y_%H%M%S.wav"))
    timestamp += count*60
    return datetime.fromtimestamp(timestamp)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for root, dirs, files in os.walk(settings.RECORDINGS_PATH):
            finaldir = os.path.split(root)[1] or os.path.split(os.path.split(root)[0])[1]
            recorder_code = finaldir[:3].upper()
            for f in files:
                if f.endswith('.wav'):
                    starttime = get_starttime(f)
                    print recorder_code, f, starttime
                    try:
                        deployment = Deployment.objects.get(recorder__code=recorder_code, start__lt=starttime, end__gt=starttime)
                        path = os.path.join(root, f)
                        try:
                            recording = Recording.objects.get(path=path)
                        except Recording.DoesNotExist:
                            recording = Recording(datetime=starttime, deployment=deployment, path=path)
                            try:
                                recording = Recording.objects.get(sha1=recording.get_hash())
                            except Recording.DoesNotExist:
                                recording.save()
                        #Now generate the snippets
                        if not recording.snippets.count():
                            f = wave.open(path, 'r')
                            try:
                                frames = f.getnframes()
                                rate = f.getframerate()
                                length = frames/float(rate)
                                snippet_length = 60
                                snippet_overlap = 0
                                snippet_minimum = 59.9
                                seconds = 0
                                while seconds + snippet_minimum < length: #Discard any snippets that are less than snippet_minimum long
                                    offset = max(seconds - snippet_overlap, 0)
                                    duration = min(snippet_length + 2*snippet_overlap, length - offset)
                                    Snippet(recording=recording, offset=offset, duration=duration).save()
                                    seconds += snippet_length
                            finally:
                                f.close()
                    except Deployment.DoesNotExist:
                        print 'No matching deployment found'
                    
