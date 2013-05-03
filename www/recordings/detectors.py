import numpy as np
from pylab import clf, specgram, savefig, mean, log
from matplotlib import mlab
from matplotlib import pyplot as plt
from datetime import datetime

from recordings.models import Snippet, Detector, Signal, Score

# Possible signals
SIGNALS = {'kiwi': 'Kiwi calls',
    'intensity': 'Mean energy'
    }

class DetectorClass(object):
    code = None
    signal = None
    version = None
    description = None

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s %s" % (self.code, self.version)

    def get_score(self, audio, *args):
        """Returns a tuple of a number and a string"""
        raise NotImplementedError

    def get_database_detector(self, add=False):
        try:
            detector = Detector.objects.get(code=self.code, version=self.version)
        except Detector.DoesNotExist:
            if add:
                try:
                    signal = Signal.objects.get(code=self.signal)
                except Signal.DoesNotExist:
                    signal = Signal(code=self.signal, description=SIGNALS[self.signal])
                    signal.save()
                detector = Detector(code=self.code,
                    signal=signal,
                    version=self.version,
                    description=self.description,
                )
                detector.save()
        return detector

    def save_score(self, snippet):
        score = self.score(snippet)
        Score(snippet=snippet,
            score = score[0],
            detector = self.get_database_detector(add=True),
        ).save()
        
        

class SimpleKiwiDetector(DetectorClass):
    code='simple-kiwi'
    signal = 'kiwi'
    description = 'Simple kiwi detector based on spectral analysis'
    version = '0.1'
    NFFT = 256

    def __unicode__(self):
        return "%s %s" % (self.code, self.version)
    
    def score(self, snippet):
        audio = snippet.get_audio()
        framerate = snippet.recording.sample_rate
        clf()
        spec = mlab.specgram(audio, NFFT=self.NFFT, Fs=framerate)
        spec2 = mlab.specgram(mean(log(spec[0][55:65,]), 0), NFFT=2048, noverlap=2000, Fs=framerate/256.0)
        max_kiwi = max(np.mean(spec2[0][20:30, ], 0))
        min_kiwi = min(np.mean(spec2[0][10:40, ], 0))
        return (max_kiwi/min_kiwi,)

class IntensityDetector(DetectorClass):
    code='intensity'
    signal = 'intensity'
    description = 'Average energy from the spectrogram'
    version = '0.1'
    NFFT = 256

    def __unicode__(self):
        return "%s %s" % (self.code, self.version)
    
    def score(self, snippet):
        audio = snippet.get_audio()
        framerate = snippet.recording.sample_rate
        clf()
        spec = mlab.specgram(audio, NFFT=self.NFFT, Fs=framerate)
        return (sum(np.min(spec[0][10:, ], 1)),)

