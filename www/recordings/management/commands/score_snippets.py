import sys
import time
import io
from contextlib import closing

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from kokako.score import Audio
from kokako.detectors.kiwi import SimpleKiwi
from kokako.detectors.intensity import Energy, LowEnergy, Amplitude

from recordings.models import Score, Recording, Snippet, Detector

BUFFER_SIZE = 1024*1024
class Command(BaseCommand):
    def handle(self, *args, **options):
        detectors = [SimpleKiwi(), Energy(), LowEnergy(), Amplitude()]
        db_detectors = []
        now = time.time()
        for detector in detectors:
            try:
                db_detectors.append(Detector.objects.get(code=detector.code, version=detector.version))
            except Detector.DoesNotExist:
                db_detectors.append(Detector(code=detector.code, 
                    version=detector.version,
                    description=detector.description))
                db_detectors[-1].save()
        detectors = zip(detectors, db_detectors)
        kiwi_detector = Detector.objects.get(code = 'simple-north-island-brown-kiwi')
        recordings = Recording.objects.all().order_by('?')
        for recording in recordings:
            snippets = Snippet.objects.filter(recording=recording).exclude(scores__detector=kiwi_detector).order_by('offset')
            if len(snippets):
                fid = io.open(recording.path, 'rb', buffering=BUFFER_SIZE)
                fid.peek(BUFFER_SIZE)
                with closing(fid):
                    for snippet in snippets:
                        count = 0
                        for detector, db_detector in detectors:
                            try:
                                audio = Audio(snippet.get_audio(fid), snippet.recording.sample_rate)
                                score = detector.score(audio)
                                if not count:   
                                    print '%s %0.1f %0.1f' % (snippet, time.time() - now, score)
                                    now = time.time()
                                try:
                                    s = Score.objects.get(detector=db_detector, snippet=snippet) 
                                    s.delete()
                                except Score.DoesNotExist:
                                    pass
                                s = Score(detector=db_detector, snippet=snippet,
                                    score=score)
                                s.save()
                            except KeyboardInterrupt:
                                raise
                            except:
                                print detector, snippet, 'Scoring failed', sys.exc_info()[0]
                            count += 1
