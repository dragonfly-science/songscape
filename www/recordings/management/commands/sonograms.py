import os
from datetime import datetime
from pylab import clf, specgram, savefig
from django.core.management.base import BaseCommand
from django.conf import settings
from recordings.models import Snippet


def save_sonogram(snippet, NFFT=256):
    clf()
    filename = "%s-%s.png" % (snippet.recording.deployment.site.code, datetime.strftime(snippet.datetime, "%Y%m%d-%H%M%S"),)
    specgram(snippet.get_audio(), NFFT=NFFT, Fs=snippet.recording.sample_rate, hold=False)
    savefig(os.path.join(settings.SONOGRAM_DIR, filename))


class Command(BaseCommand):
    def handle(self, *args, **options):
        snippets = Snippet.objects.filter(sonogram='')
        for snippet in snippets:
            save_sonogram(snippet)

        
