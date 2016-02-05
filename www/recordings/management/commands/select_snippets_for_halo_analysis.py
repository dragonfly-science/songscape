import random
import shutil

from django.core.management.base import BaseCommand, CommandError

from www.recordings.models import Snippet, Analysis, AnalysisSet, Detector, Score, Deployment, Recording

class Command(BaseCommand):
    def handle(self, *args, **options):
        analysis = Analysis.objects.get(code='rimutaka-kiwi')
        deployments = Deployment.objects.all()
        clipping = Detector.objects.get(code='amplitude')
        #code = 'simple-north-island-brown-kiwi'
        version = '0.1.2'
        #detector = Detector.objects.get(code=code, version=version)
	instance = Recording.objects.values_list('datetime')[0]
	recording_datetime = instance[0]
	recording = Recording.objects.all()
        for deployment in deployments:
            snippets = Snippet.objects.all()
	    n_snippets = snippets.count()
	    '''
	    # get unclipped_snippets
            snippets = Snippet.objects.\
                filter(recording__deployment=deployment).\
                filter(scores__detector = detector, scores__score__lt = 1e10).\
                filter(scores__detector = \
                    Detector.objects.get(code='amplitude'), scores__score__lt=32000) 
            n_snippets = snippets.count()
            random_already = snippets.filter(sets__analysis=analysis, 
                sets__selection_method=u'Randomly selected 2%')
            kiwi_already = snippets.filter(sets__analysis=analysis, 
                sets__selection_method=u'Simple NIBK score higher than 25 ')
            already = snippets.filter(sets__analysis=analysis)

            #Now select a random 2%
            random_snippets = []
            if len(random_already) < round(0.02*n_snippets):
                random_snippets = list(snippets.\
                    exclude(id__in=already).\
                    exclude(id__in=kiwi_snippets).\
                    order_by('?')[:(round(n_snippets*0.02) - len(random_already))])
	    '''
	   
            #Select only morning recordings
	    morn_recordings = []
	    for r in recording_datetime:
		recording_hour = r.hour
		if recordings_start < 11 and recordings_start > 06:		
			morn_recordings = morn_recordings.append(recording_file)

	    #Select a random 5 snippets
	    random_snippets = []
	    five_snippets = []
	    for recording_file in recording:
		random_snippets = list(snippets.order_by('?'))
		five_snippets = random_snippets[0:5]

            snippet_set = zip(random_snippets, ['Randomly selected 2%']*len(random_snippets)) +\
                zip(list(kiwi_snippets), ['Simple NIBK score higher than 25 ']*len(kiwi_snippets))
            random.shuffle(snippet_set)

            print deployment, n_snippets, len(already), len(kiwi_snippets), len(random_snippets)
            for snip, reason in snippet_set:
                AnalysisSet(analysis=analysis, snippet=snip, selection_method=reason).save()

