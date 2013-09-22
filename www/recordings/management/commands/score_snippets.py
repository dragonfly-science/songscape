import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recordings.models import Score, Recording, Snippet, Detector
from kokako.score import Audio
from kokako.detectors.kiwi import SimpleKiwi
from kokako.detectors.intensity import Energy, LowEnergy, Amplitude


class Command(BaseCommand):
    def handle(self, *args, **options):
        detectors = [SimpleKiwi(), Energy(), LowEnergy(), Amplitude()]
        db_detectors = []
        for detector in detectors:
            try:
                db_detectors.append(Detector.objects.get(code=detector.code, version=detector.version))
            except Detector.DoesNotExist:
                db_detectors.append(Detector(code=detector.code, 
                    version=detector.version,
                    description=detector.description))
                db_detectors[-1].save()
        detectors = zip(detectors, db_detectors)

        snippets = Snippet.objects.all()[1:10]
        for snippet in snippets:
            for detector, db_detector in detectors:
                #try:
                audio = Audio(snippet.get_audio(), snippet.recording.sample_rate)
                score = detector.score(audio)
                try:
                    s = Score.objects.get(detector=db_detector, snippet=snippet) 
                    s.delete()
                except Score.DoesNotExist:
                    pass
                s = Score(detector=db_detector, snippet=snippet,
                    score=score)
                s.save()
                print detector, snippet, snippet.scores.latest('datetime').score
#                except:
#                    print detector, snippet, 'Scoring failed', sys.exc_info()[0]
                
