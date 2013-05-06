import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recordings.models import Score, Recording, Snippet, Signal, Detector
from recordings.detectors import SimpleKiwiDetector, IntensityDetector

detectors = (SimpleKiwiDetector(), IntensityDetector())


class Command(BaseCommand):
    def handle(self, *args, **options):
        for detector in detectors:
            snippets = Snippet.objects.exclude(scores__detector=detector.get_database_detector())
            for snippet in snippets:
                try:
                    detector.save_score(snippet)
                    print detector, snippet, snippet.scores.latest('datetime').score
                except:
                    print detector, snippet, 'Scoring failed', sys.exc_info()[0]
                
