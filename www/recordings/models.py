import hashlib
import os
import wave
import numpy as np
import struct
import datetime
from contextlib import closing
from cStringIO import StringIO

# matplotlib breaks mod_wsgi due to some circular imports, which
# means the first time it loads cbook isn't found, but it works afterwards!
# Newer versions of matplotlib probably fix this, but it's easier to
# rely on the ubuntu python-matplotlib package during deployment.
import matplotlib.cbook
from pylab import figure, specgram, savefig, close, gca, clf

from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify



class SlugMixin(object):
    """ automatically generate slug when object is initially created """
    def generate_slug(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = self.generate_slug()

        super(SlugMixin, self).save(*args, **kwargs)


class UniqueSlugMixin(SlugMixin):
    ''' generate a unique slug '''
    def is_unique_slug(self, slug):
        qs = self.__class__.objects.filter(code=slug)
        return not qs.exists()
 
    def generate_slug(self):
        original_slug = super(UniqueSlugMixin, self).generate_slug()
        slug = original_slug
 
        iteration = 1
        while not self.is_unique_slug(slug):
            slug = "%s-%d" % (original_slug, iteration)
            iteration += 1
 
        return slug


class Organisation(models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class Site(models.Model):
    code = models.SlugField(max_length=32) 
    name = models.TextField(null=True, blank=True) 
    organisation = models.ForeignKey(Organisation, related_name='sites')
    description = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    
    def __unicode__(self):
        return '%s-%s' % (self.organisation.code, self.code)

    class Meta:
        unique_together = (('code', 'organisation'),)

class Recorder(models.Model):
    code = models.SlugField(max_length=32)
    organisation = models.ForeignKey(Organisation, related_name='recorders')
    comments = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.organisation.code, self.code)

    class Meta:
        unique_together = (('code', 'organisation'),)

class Deployment(models.Model):
    site = models.ForeignKey(Site, related_name='deployments')
    recorder = models.ForeignKey(Recorder, related_name='deployments')
    owner = models.ForeignKey(Organisation, related_name='deployments')
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return '%s %s %s'%(self.site, self.recorder, self.start)
    
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

    def _get_frames(self, offset, duration):
        with closing(wave.open(self.path, 'r')) as wav:
            wav.rewind()
            if offset:
                wav.readframes(int(offset*self.sample_rate*self.nchannels)) #Read to the offset in seconds
            if not duration:
                duration = self.duration - offset
            frames = wav.readframes(int(duration*self.sample_rate*self.nchannels))
        return frames

    def get_audio(self, offset=0, duration=0):
        """Returns the audio associated with a snippet"""
        frames = self._get_frames(offset, duration)
        return np.array(struct.unpack_from ("%dh" % (len(frames)/2,), frames))


class Tag(UniqueSlugMixin, models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=30)
   
    def __unicode__(self):
        return '%s' % (self.code)


class Snippet(models.Model):
    recording = models.ForeignKey(Recording, related_name='snippets')
    offset = models.FloatField() #seconds
    duration = models.FloatField()
    sonogram = models.ImageField(upload_to=settings.SONOGRAM_DIR, null=True, blank=True) 
    soundcloud = models.IntegerField(null=True, blank=True)
    soundfile = models.FileField(upload_to=settings.MP3_DIR, null=True, blank=True)
    
    class Meta:
        unique_together = (('recording', 'offset', 'duration'),)
    
    def __unicode__(self):
        return '%s-%s-%s'%(self.recording.deployment.recorder, 
            datetime.datetime.strftime(self.datetime, '%Y%m%d-%H%M%S'), self.duration
        )
    
    def get_audio(self):
        return self.recording.get_audio(self.offset, self.duration)

    def save_sonogram(self, replace=False, NFFT=512):
        if not self.sonogram or \
                replace or \
                (self.sonogram and not os.path.exists(self.sonogram.path)):
            clf()
            fig = figure(figsize=(10, 5))
            filename = "%s.png" % (self,)
            specgram(self.get_audio(), 
                NFFT=NFFT, 
                Fs=self.recording.sample_rate, 
                hold=False)
            string_buffer = StringIO()
            gca().set_ylabel('Frequency (Hz)')
            gca().set_xlabel('Time (s)')
            savefig(string_buffer, format='png')
            imagefile = ContentFile(string_buffer.getvalue())
            if self.sonogram:
                self.sonogram.delete()
            self.sonogram.save(filename, imagefile, save=True)
            close()
        return self.sonogram

    def url_path(self):
        full_path = self.recording.path
        # hack hack
        return '/media/' + full_path.split('songscape/')[1]

    def end_time(self):
        return self.offset + self.duration

    @property
    def datetime(self):
        return self.recording.datetime + datetime.timedelta(seconds=self.offset)


class Signal(models.Model):
    code = models.SlugField(max_length=32, unique=True) 
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.code

class Detector(models.Model):
    code = models.SlugField(max_length=32) 
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
    

class Analysis(SlugMixin, models.Model):
    name = models.CharField(max_length=32)
    code = models.SlugField(max_length=32)
    description = models.TextField(default="")
    datetime = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    ubertag = models.ForeignKey(Tag, related_name="ubertags", null=True, blank=True)
    deployments = models.ManyToManyField(Deployment)
    detectors = models.ManyToManyField(Detector)
    organisation = models.ForeignKey(Organisation, related_name="analyses")
    
    class Meta:
        unique_together = (('organisation', 'code'),)

    def __unicode__(self):
        return '%s' % (self.name)

    def normal_tags(self):
        return self.tags.all().exclude(id__exact=self.ubertag.id)


class Identification(models.Model):
    user = models.ForeignKey(User)
    analysis = models.ForeignKey(Analysis)
    snippet = models.ForeignKey(Snippet)
    scores = models.ManyToManyField(Score)  # This holds the list of scores that the user saw when they made the identification
    true_tags = models.ManyToManyField(Tag, related_name="true_tags")
    false_tags = models.ManyToManyField(Tag, related_name="false_tags")
    comment = models.TextField(default="")

