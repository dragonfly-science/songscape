import numpy as np
from pylab import clf, specgram, savefig, mean, log
from matplotlib import mlab
from matplotlib import pyplot as plt

# Possible signals
signal = {'kiwi': 'Kiwi calls',
    'intensity': 'Mean energy'
    }


class Detector(object):
    code = None
    name = None
    signal = None
    version = None
    description = None

    def get_score(self, audio, *args):
        """Returns a tuple of a number and a string"""
        raise NotImplementedError

class SimpleKiwiDetector(Detector):
    code='simple-kiwi'
    signal = 'kiwi'
    description = 'Simple kiwi detector based on spectral analysis'
    version = '0.1'
    self.NFFT = 256

    def get_score(self, audio, framerate):
        clf()
        spec = mlab.specgram(audio, NFFT=self.NFFT, Fs=framerate)
        spec2 = mlab.specgram(mean(log(spec[0][55:65,]), 0), NFFT=2048, noverlap=2000, Fs=framerate/256.0)
        max_kiwi = max(np.mean(spec2[0][20:30, ], 0))
        min_kiwi = min(np.mean(spec2[0][10:40, ], 0))
        return max_kiwi/min_kiwi, ''

class IntensityDetector(Detector):
    code='intensity'
    signal = 'intensity'
    description = 'Average energy from the spectrogram'
    version = '0.1'
    self.NFFT = 256

    def get_score(self, audio, framerate):
        clf()
        spec = mlab.specgram(audio, NFFT=self.NFFT, Fs=framerate)
        return sum(np.min(spec[0][10:, ], 1)), ''



