import hashlib

from django.db import models
from django.conf import settings

class Organisation(models.Model):
    code = models.SlugField(max_length=20, unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

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
    
    class Meta:
        unique_together = (('datetime', 'deployment'),)

    def save(self, *args, **kwargs):
        "Given a path, datetime, and a deployment, saves the recording and populates the other data"
        wav = wave.open(self.path)
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
        self.sample_rate = framerate
        self.duration = nframes/float(framerate)
        self.nchannels = nchannels
        hasher = hashlib.sha1()
        hasher.update(open(self.path).read(2000))
        self.sha1 = hasher.hexdigest()
        super(Recording).save(self, *args, **kwargs)

    def get_audio(self, offset=0, duration=0):
        """Returns the audio associated with a snippet"""
        wav = wave.open(self.path)
        if offset:
            wav.readframes(offset*self.sample_rate*self.nchannels) #Read to the offset in seconds
        if not duration:
            duration = self.duration - offset
        frames = wav.readframes(duration*self.sample_rate*self.nchannels)
        audio = np.array(struct.unpack_from ("%dh" % (len(frames)/2,), frames))
        return audio

class Snippet(models.Model):
    recording = models.ForeignKey(Recording, related_name='snippets')
    offset = models.FloatField()
    duration = models.FloatField()
    sonogram = models.ImageField(upload_to=settings.SONOGRAM_DIR, null=True, blank=True) 
    soundcloud = models.IntegerField(null=True, blank=True)
    
    def get_audio(self):
        return self.recording.get_audio(self.offset, self.duration)

class Signal(models.Model):
    code = models.SlugField(max_length=20) 
    description = models.TextField(null=True, blank=True)

class Detector(models.Model):
    code = models.SlugField(max_length=20) 
    signal = models.ForeignKey(Signal, related_name='detectors')
    description = models.TextField(null=True, blank=True)
    version = models.TextField()

class Score(models.Model):
    snippet = models.ForeignKey(Snippet, related_name='scores')
    detector = models.ForeignKey(Detector, related_name='scores')
    score = models.FloatField(null=True, blank=True)
    description = models.TextField(default="")
    datetime = models.DateTimeField()

    class Meta:
        unique_together = (('snippet', 'detector'),)


    
