import hashlib
import wave
import numpy as np
import struct
import datetime

from django.db import models
from django.conf import settings

class Organisation(models.Model):
    code = models.SlugField(max_length=20, unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class Site(models.Model):
    code = models.SlugField(max_length=20, unique=True) 
    name = models.TextField(null=True, blank=True) 
    description = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    
    def __unicode__(self):
        return self.code

class Recorder(models.Model):
    code = models.SlugField(max_length=20)
    organisation = models.ForeignKey(Organisation, related_name='recorders')
    comments = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.code

    class Meta:
        unique_together = (('code', 'organisation'),)

class Deployment(models.Model):
    site = models.ForeignKey(Site, related_name='deployments')
    recorder = models.ForeignKey(Recorder, related_name='deployments')
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return '%s %s %s'%(self.site.code, self.recorder.code, self.start)
    
    class Meta:
        unique_together = (('site', 'recorder', 'start'),)

class Recording(models.Model):
    datetime = models.DateTimeField()
    deployment = models.ForeignKey(Deployment, related_name='recordings')
    sha1 = models.TextField()
    sample_rate = models.IntegerField()
    duration = models.FloatField()
    nchannels = models.IntegerField()
    path = models.TextField()
    
    def __unicode__(self):
        return '%s %s %s'%(self.deployment.site.code, self.deployment.recorder.code, self.datetime)
    
    class Meta:
        unique_together = (('datetime', 'deployment'),)

    def get_hash(self):
        hasher = hashlib.sha1()
        hasher.update(open(self.path).read(2000))
        return hasher.hexdigest()

    def verify_hash(self):
        return self.sha1 == self.get_hash()

    def already_exists(self):
        try:
            Recording.objects.get(sha1=self.get_hash())
            return True
        except Recording.DoesNotExistError:
            return False

    def save(self, *args, **kwargs):
        "Given a path, datetime, and a deployment, saves the recording and populates the other data"
        wav = wave.open(self.path)
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
        self.sample_rate = framerate
        self.duration = nframes/float(framerate)
        self.nchannels = nchannels
        self.sha1 = self.get_hash()
        super(Recording, self).save(*args, **kwargs)

    def get_audio(self, offset=0, duration=0):
        """Returns the audio associated with a snippet"""
        wav = wave.open(self.path, 'r')
        if offset:
            wav.readframes(int(offset*self.sample_rate*self.nchannels)) #Read to the offset in seconds
        if not duration:
            duration = self.duration - offset
        frames = wav.readframes(int(duration*self.sample_rate*self.nchannels))
        audio = np.array(struct.unpack_from ("%dh" % (len(frames)/2,), frames))
        return audio

class Snippet(models.Model):
    recording = models.ForeignKey(Recording, related_name='snippets')
    offset = models.FloatField() #seconds
    duration = models.FloatField()
    sonogram = models.ImageField(upload_to=settings.SONOGRAM_DIR, null=True, blank=True) 
    soundcloud = models.IntegerField(null=True, blank=True)
    soundfile = models.FileField(upload_to=settings.MP3_DIR, null=True, blank=True)
    
    def __unicode__(self):
        return '%s (%s s)' % (self.recording, self.offset)
    
    def get_audio(self):
        return self.recording.get_audio(self.offset, self.duration)

    @property
    def datetime(self):
        return self.recording.datetime + datetime.timedelta(seconds=self.offset)

class Signal(models.Model):
    code = models.SlugField(max_length=20) 
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.code

class Detector(models.Model):
    code = models.SlugField(max_length=20) 
    signal = models.ForeignKey(Signal, related_name='detectors')
    description = models.TextField(null=True, blank=True)
    version = models.TextField()

    def __unicode__(self):
        return '%s %s' % (self.code, self.version)
    
    class Meta:
        unique_together = (('code', 'version'),)

class Score(models.Model):
    snippet = models.ForeignKey(Snippet, related_name='scores')
    detector = models.ForeignKey(Detector, related_name='scores')
    score = models.FloatField(null=True, blank=True)
    description = models.TextField(default="")
    datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s (%s)' % (self.score, self.description)
    
    class Meta:
        unique_together = (('snippet', 'detector'),)


    
