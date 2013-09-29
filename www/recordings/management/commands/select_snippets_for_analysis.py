import random

from django.core.management.base import BaseCommand, CommandError

from www.recordings.models import Snippet, Analysis, AnalysisSet, Detector, Score, Deployment

class Command(BaseCommand):
    def handle(self, *args, **options):
        analysis = Analysis.objects.get(code='rimutaka-kiwi')
        deployments = Deployment.objects.all()
        clipping = Detector.objects.get(code='amplitude')
        for deployment in deployments:
            # get unclipped_snippets
            unclipped_scores = Score.objects.filter(detector=clipping, score__lt=32000)
            unclipped_snippets = Snippet.objects.filter(scores__in=unclipped_scores, recording__deployment=deployment)
        
            n_snippets = unclipped_snippets.count()
            random_already = AnalysisSet.objects.filter(snippet__in=unclipped_snippets, 
                analysis=analysis, 
                selection_method=u'Randomly selected 2%')
            kiwi_already = AnalysisSet.objects.filter(snippet__in=unclipped_snippets, 
                analysis=analysis, 
                selection_method=u'Simple NIBK score higher than 25 ')
            already = AnalysisSet.objects.filter(snippet__in=unclipped_snippets, 
                analysis=analysis)
            already_list = set([x.snippet.id for x in already])
            kiwi_already_list = set([x.snippet.id for x in kiwi_already])
            random_already_list = set([x.snippet.id for x in random_already])
            duplicates = kiwi_already_list.intersection(random_already_list)
            if duplicates:
                print 'Remove %s duplicates' % len(duplicates)
                #Make sure that we are depuped (not adding a snippet twice)
                for snip_id in kiwi_already_list.intersection(random_already_list):
                    aset = AnalysisSet.objects.get(snippet__id=snip_id, 
                        analysis=analysis, 
                        selection_method=u'Randomly selected 2%')
                    aset.delete()
                    random_already_list.remove(snip_id)
            #select by kiwi score
            kiwi = Detector.objects.get(code='simple-north-island-brown-kiwi')
            kiwi_scores = Score.objects.filter(detector=kiwi, score__gt=25).exclude(score='NaN')
            kiwi_snippets = list(unclipped_snippets.filter(scores__in=kiwi_scores).exclude(id__in=already_list))

            #Now select a random 2%
            random_snippets = []
            if len(random_already_list) < round(0.02*n_snippets):
                random_snippets = list(unclipped_snippets.\
                    exclude(id__in=already_list).\
                    exclude(id__in=[x.id for x in kiwi_snippets]).\
                    order_by('?')[:(round(n_snippets*0.02) - len(random_already_list))])

            snippet_set = zip(random_snippets, ['Randomly selected 2%']*len(random_snippets)) +\
                zip(kiwi_snippets, ['Simple NIBK score higher than 25 ']*len(kiwi_snippets))
            random.shuffle(snippet_set)

            print deployment, n_snippets, len(already_list), len(kiwi_snippets), len(random_snippets)
            for snip, reason in snippet_set:
                AnalysisSet(analysis=analysis, snippet=snip, selection_method=reason).save()



