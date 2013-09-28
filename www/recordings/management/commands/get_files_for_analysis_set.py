import random

from django.core.management.base import BaseCommand, CommandError

from www.recordings.models import Snippet, Analysis, AnalysisSet, Detector, Score

class Command(BaseCommand):
    def handle(self, *args, **options):
        analysis = Analysis.objects.get(code='rimutaka-kiwi')
        snippets = [x.snippet for x in AnalysisSet.objects.filter(analysis=analysis)]
        count = 0
        for snippet in snippets:
            count += 1
            print len(snippets), count
            snippet.save_sonogram()
            snippet.save_soundfile()



