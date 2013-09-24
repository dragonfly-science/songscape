import random

from django.core.management.base import BaseCommand, CommandError

from recordings.models import Snippet, Analysis, AnalysisSet, Detector, Score

class Command(BaseCommand):
    def handle(self, *args, **options):
        analysis = Analysis.objects.get(code='rimutaka-kiwi')
        # get unclipped_snippets
        clipping = Detector.objects.get(code='amplitude')
        unclipped_scores = Score.objects.filter(detector=clipping, score__lt=32000)
        unclipped_snippets = Snippet.objects.filter(scores__in=unclipped_scores)
        
        n_snippets = unclipped_snippets.count()

        #select a random 1%
        random_snippets = unclipped_snippets.order_by('?')[:n_snippets*0.02]
        random_snippets = zip(list(random_snippets), ['Randomly selected 2%']*len(random_snippets))

        #select by kiwi score
        kiwi = Detector.objects.get(code='simple-north-island-brown-kiwi')
        kiwi_scores = Score.objects.filter(detector=kiwi, score__gt=25).exclude(score='NaN')
        kiwi_snippets = unclipped_snippets.filter(scores__in=kiwi_scores)
        kiwi_snippets = zip(list(kiwi_snippets), ['Simple NIBK score higher than 25 ']*len(kiwi_snippets))

        snippet_set = random_snippets + kiwi_snippets
        random.shuffle(snippet_set)
            
        for snip, reason in snippet_set:
            AnalysisSet(analysis=analysis, snippet=snip, selection_method=reason).save()



