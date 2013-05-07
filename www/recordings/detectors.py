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

    def get_database_detector(self, add=True):
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
            else:
                raise
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
    version = '0.1.1'
    window = 0.032
    lower_call_frequency = 1600
    upper_call_frequency = 2200
    lower_syllable_frequency = 0.5
    upper_syllable_frequency = 1.1

    def __unicode__(self):
        return "%s %s" % (self.code, self.version)
    
    def score(self, snippet):
        audio = snippet.get_audio()
        framerate = snippet.recording.sample_rate
        NFFT = int(self.window*framerate)
        clf()
        spec = mlab.specgram(audio, NFFT=NFFT, noverlap=NFFT/2, Fs=framerate)
        freqs = np.where((spec[1] >= self.lower_call_frequency)*(spec[1] <= self.upper_call_frequency))
        spec2 = mlab.specgram(mean(log(spec[0][freqs[0],]), 0), NFFT=1024, noverlap=512, Fs=2/self.window)
        freqs2 = np.where((spec2[1] >= self.lower_syllable_frequency)*(spec2[1] <= self.upper_syllable_frequency))
        max_kiwi = max(np.max(spec2[0][freqs2[0],:], 0))
        mean_kiwi = np.exp(np.mean(np.mean(np.log(spec2[0][freqs2[0], :]), 0)))
        return (max_kiwi/mean_kiwi,)

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

