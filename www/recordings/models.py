from django.db import models
from django.conf import settings

class Organisation(models.Model):
    code = models.CharField(max_length=10)
    name = models.TextField()

class Site(models.Model):
    code = models.CharField(max_length = 10) 
    comments = models.TextField(null=True,blank=True)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    altitude = models.FloatField(null=True,blank=True)
    
    def __unicode__(self):
        return self.code

class Recorder(models.Model):
    code = models.CharField(max_length = 10)
    organisation = models.ForeignKey(Organisation)
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
        return self.code

class Deployment(models.Model):
    site = models.ForeignKey(Site)
    recorder = models.ForeignKey(Recorder)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True,blank=True)
#    duration1 = models.IntegerField()
#    start1 = models.TimeField()
#    duration2 = models.IntegerField()
#    start2 = models.TimeField()
    comments = models.TextField(null=True,blank=True)
    
    def __unicode__(self):
        return '%s %s %s'%(self.site.code, self.recorder.code, self.start)

class SoundFile(models.Model)
    datetime = models.DateTimeField()
    deployment = models.ForeignKeyField(Deployment)
    sha1 = models.TextField()
    sample_rate = models.IntegerField()
    duration = models.FloatField()
    nchannels = models.IntegerFieldField()
    path = models.TextField()

    def __save__(self):
        wav = wave.open(self.path)
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
        self.sample_rate = framerate
        self.duration = nframes/float(framerate)
        self.nchannels = nchannels

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
    sound_file = modles.ForeignKey(SoundFile)
    offset = models.FloatField()
    duration = models.FloatField()
    sonogram = models.ImageField(upload_to=settings.SONOGRAM_DIR, null=True, blank=True) 
    mp3 = models.FileField(upload_to=settings.MP3_DIR, null=True, blank=True) 
    
    def get_audio(self):
        return self.sound_file.get_audio(self.offset, self.duration)

class Score(models.Model):
    snippet = models.ForeignKey(Snippet)
    scorer = models.ForeignKey(Scorer)
    score = models.FloatField(null=True, blank=True)

class Scorer(models.Model):
    name = models.SlugField()
    description = models.TextField()
    version = models.TextField()
    code = models.TextField()



