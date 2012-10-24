import csv
from datetime import datetime
from optparse import make_option
import os
import struct
from time import time, strptime, mktime
import wave

import numpy as np
from pylab import clf, specgram, savefig, mean, log
from matplotlib import mlab
from matplotlib import pyplot as plt


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recordings.models import Score, Deployment

def kiwi_index(audio, framerate, NFFT=256):
    """Returns an index of whether an audio clip contains a kiwicall. The higher the  index the more the signal if
    like a kiwi"""
    clf()
    spec = mlab.specgram(audio, NFFT=NFFT, Fs=framerate)
    spec2 = mlab.specgram(mean(log(spec[0][55:65,]), 0), NFFT=2048, noverlap=2000, Fs=framerate/256.0)
    max_kiwi = max(np.mean(spec2[0][20:30, ], 0))
    min_kiwi = min(np.mean(spec2[0][10:40, ], 0))
    return max_kiwi/min_kiwi, spec

def intensity_index(spec):
    """Returns an index that is related to the background noise in an audio clip"""
    return sum(np.min(spec[0][10:, ], 1))

def get_starttime(filename, count=0):
    """returns the start time, by parsing the filename of a WAV file from the DOC recorders"""
    timestamp = mktime(strptime(filename, "%d%m%y_%H%M%S.wav"))
    timestamp += count*60
    return datetime.fromtimestamp(timestamp)

def get_minute(path):
    """An iterator that returns a minute long soundclip from a WAV file each time that it is called"""
    wav = wave.open(path)
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    minute = framerate*60
    while True:
        try:
            frames =  wav.readframes(minute*nchannels)
            audio = np.array(struct.unpack_from ("%dh" % (len(frames)/2,), frames))
            if not audio.shape[0]:
                raise StopIteration, 'Empty audio'
            yield audio, framerate
        except Exception, message:
            print message
            wav.close()
            raise StopIteration

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            raise ValueError, 'Please supply the path to the root directory of the files you want to process'
        for root, dirs, files in os.walk(args[0]):
            finaldir = os.path.split(root)[1] or os.path.split(os.path.split(root)[0])[1]
            for f in files:
                if f.endswith('.wav'):
                    for count, minute in enumerate(get_minute(os.path.join(root, f))):
                        starttime = get_starttime(f, count)
                        kiwi, spec = kiwi_index(*minute)
                        energy = intensity_index(spec)
                        print finaldir, f, count, starttime, kiwi, energy
                        try:
                            #deployment = Deployment.objects.get(recorder__code=finaldir[:3].upper(), start__lt=starttime, end__gt=starttime)
                            deployment = Deployment.objects.filter(recorder__code=finaldir[:3].upper())[0]
                        except:
                            print 'No matching deployment found'
                            deployment = None
                        if deployment:
                            try:
                                score = Score(filename=f, deployment=deployment, datetime=starttime, kiwi_index=kiwi, energy_index=energy)
                                if kiwi > 5:
                                    fig_file = "%s-%s.png" % (deployment.site.code, datetime.strftime(starttime, "%Y%m%d-%H%M%S"),)
                                    clf()
                                    specgram(minute[0], NFFT=256, Fs=minute[1], hold=False)
                                    savefig(os.path.join(settings.SONOGRAM_DIR, fig_file))
                                    score.sonogram = fig_file
                                score.save()
                            except Exception, message:
                                print message


