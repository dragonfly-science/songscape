import hashlib
import os
import wave
import numpy as np
import struct
import datetime
from cStringIO import StringIO
from tempfile import TemporaryFile

# matplotlib breaks mod_wsgi due to some circular imports, which
# means the first time it loads cbook isn't found, but it works afterwards!
# Newer versions of matplotlib probably fix this, but it's easier to
# rely on the ubuntu python-matplotlib package during deployment.
import matplotlib
matplotlib.use('Agg')
import matplotlib.cbook
from pylab import figure, specgram, savefig, close, gca, clf, cm

from django.core.files.base import ContentFile
from django.core.files import File
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from www.recordings.templatetags.recording_filters import wav_name, sonogram_name, snippet_name
import wavy


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
    code = models.SlugField(max_length=64, unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class Site(models.Model):
    code = models.SlugField(max_length=64)
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
    code = models.SlugField(max_length=64)
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
        return '%s-%s-%s-%s'%(self.site,
            datetime.datetime.strftime(self.start, '%Y%m%d-%H%M%S'),
            datetime.datetime.strftime(self.end, '%Y%m%d-%H%M%S'),
            self.recorder,
        )

    class Meta:
        #TODO: Check that recorder codes and site codes are unique ...
        #e.g.:  unique_together = (('site__code', 'recorder__code', 'start'),)
        unique_together = (('site', 'recorder', 'start'),)

class Recording(models.Model):
    datetime = models.DateTimeField()
    deployment = models.ForeignKey(Deployment, related_name='recordings')
    md5 = models.TextField()
    framerate = models.IntegerField()
    sampwidth = models.IntegerField()
    duration = models.FloatField()
    nchannels = models.IntegerField()
    path = models.TextField()

    def __unicode__(self):
        return '%s-%s-%s'%(self.deployment.site.code, self.deployment.recorder.code, self.datetime)

    class Meta:
        unique_together = (('datetime', 'deployment'),)

    def get_hash(self):
        hasher = hashlib.md5()
        hasher.update(open(self.path).read())
        return hasher.hexdigest()

    def verify_hash(self):
        return self.md5 == self.get_hash()

    def already_exists(self):
        try:
            Recording.objects.get(md5=self.get_hash())
            return True
        except Recording.DoesNotExistError:
            return False

    def save(self, *args, **kwargs):
        "Given a path, datetime, and a deployment, saves the recording and populates the other data"
        wav = wave.open(self.path)
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
        self.framerate = framerate
        self.sampwidth = sampwidth
        self.duration = nframes/float(framerate*nchannels)
        self.nchannels = nchannels
        self.md5 = kwargs.get('md5', self.get_hash())
        super(Recording, self).save(*args, **kwargs)


    def get_audio(self, offset=0, duration=0):
        audio, framerate = wavy.get_audio(self.path, offset=offset, duration=duration)
        return audio

class Tag(UniqueSlugMixin, models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.TextField()

    def __unicode__(self):
        return '%s' % (self.code)


class Snippet(models.Model):
    recording = models.ForeignKey(Recording, related_name='snippets')
    offset = models.FloatField() #seconds
    duration = models.FloatField()
    sonogram = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, settings.SONOGRAM_DIR), null=True, blank=True)
    soundcloud = models.IntegerField(null=True, blank=True)
    soundfile = models.FileField(upload_to=os.path.join(settings.MEDIA_ROOT, settings.SNIPPET_DIR), null=True, blank=True)

    class Meta:
        unique_together = (('recording', 'offset', 'duration'),)

    def __unicode__(self):
        return snippet_name(self)

    def get_audio(self):
        if self.soundfile and os.path.exists(self.soundfile.path):
            audio, framerate = wavy.get_audio(self.soundfile.path)
            return audio
        else:
            return self.recording.get_audio(self.offset, self.duration)

    def save_sonogram(self, replace=False, NFFT=512):
        if not self.sonogram or \
                replace or \
                (self.sonogram and not os.path.exists(self.sonogram.path)):
            clf()
            fig = figure(figsize=(10, 5))
            filename = self.get_sonogram_name()
            specgram(self.get_audio(),
                NFFT=NFFT,
                Fs=self.recording.framerate,
                hold=False,
                cmap=cm.gray)
            string_buffer = StringIO()
            gca().set_ylabel('Frequency (Hz)')
            gca().set_xlabel('Time (s)')
            savefig(string_buffer, format='png')
            imagefile = ContentFile(string_buffer.getvalue())
            if self.sonogram:
                try:
                    self.sonogram.delete()
                except:
                    pass
            self.sonogram.save(filename, imagefile, save=False)
            self.sonogram.name = os.path.join(settings.SONOGRAM_DIR, filename)
            close()

    def save_soundfile(self, replace=False):
        if not self.soundfile or \
                replace or \
                (self.soundfile and not os.path.exists(self.soundfile.path)):
            filename = self.get_soundfile_name()
            wav_file = TemporaryFile()
            wavy.slice_wave(self.recording.path, wav_file, self.offset, self.duration)
            wav_file.seek(0)
            self.soundfile.save(filename, File(wav_file, name=filename), save=False)
            self.soundfile.name = os.path.join(settings.SNIPPET_DIR, filename)
            self.save()

    def url_path(self):
        full_path = self.recording.path
        # hack hack
        return '/media/' + full_path.split('songscape/')[1]

    def end_time(self):
        return self.offset + self.duration

    def get_sonogram_name(self):
        return sonogram_name(self)

    def get_soundfile_name(self):
        return wav_name(self)

    @property
    def datetime(self):
        return self.recording.datetime + datetime.timedelta(seconds=self.offset)

    def count_tag(self, tag, **kwargs):
        identifications = Identification.objects.filter(snippet=self, **kwargs)
        positive = 0
        negative = 0
        for identification in identifications:
            if tag in identification.true_tags.all():
                positive += 1
            if tag in identification.false_tags.all():
                negative += 1
        return positive, negative, len(identifications)

class Detector(models.Model):
    code = models.SlugField(max_length=64)
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
    name = models.TextField()
    code = models.SlugField(max_length=64, unique=True)
    description = models.TextField(default="")
    datetime = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    ubertag = models.ForeignKey(Tag, related_name="ubertags", null=True, blank=True)  #TODO: Rename to default_tag, related_name="analyses_default"
    snippets = models.ManyToManyField(Snippet, through='AnalysisSet', related_name="analyses")
    organisation = models.ForeignKey(Organisation, related_name="analyses") #Replace with user

    class Meta:
        unique_together = (('organisation', 'code'),)

    def __unicode__(self):
        return '%s' % (self.name)

    def normal_tags(self):
        return self.tags.all().exclude(id__exact=self.ubertag.id)

class AnalysisSet(models.Model):
    analysis = models.ForeignKey(Analysis, related_name="set")
    snippet = models.ForeignKey(Snippet, related_name="set")
    selection_method = models.TextField(default="")


class Identification(models.Model):
    user = models.ForeignKey(User, related_name="identifications")
    analysis = models.ForeignKey(Analysis, related_name="identifications")
    datetime = models.DateTimeField(auto_now=True)
    snippet = models.ForeignKey(Snippet, related_name="identifications")
    scores = models.ManyToManyField(Score)  # This holds the list of scores that the user saw when they made the identification
    true_tags = models.ManyToManyField(Tag, related_name="identifications")
    false_tags = models.ManyToManyField(Tag, related_name="negative_identifications")
    comment = models.TextField(default="")

