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
from pylab import figure, specgram, savefig, close, gca, clf, cm,\
    where, logical_and, percentile, imshow, log10, flipud, rcParams

from django.core.files.base import ContentFile
from django.core.files import File
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.exceptions import SuspiciousOperation
from django.utils.timezone import utc


from www.recordings.templatetags.recording_filters import wav_name, sonogram_name, \
    snippet_name, isotime, timezone_lookup
import wavy
import pytz

rcParams['font.size'] = 10

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
    recorder = models.ForeignKey(Recorder, related_name='deployments', null=True, blank=True)
    owner = models.ForeignKey(Organisation, related_name='deployments')
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    start_timezone = models.TextField()

    def __unicode__(self):
        return '%s-%s-%s-%s'%(self.owner.code, self.site,
            isotime(self.start),
            isotime(self.end)
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
        return '%s-%s-%s'%(self.deployment.owner.code, self.deployment.site.code, isotime(self.datetime))

    #class Meta:
    #    unique_together = (('datetime', 'deployment'),)

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

    def get_canonical_path(self):
        owner_dir = self.deployment.owner.code
        deployment_dir = "%s-%s" % (self.deployment.site.code, 
            self.deployment.start.\
                astimezone(pytz.timezone(self.deployment.start_timezone)).\
                strftime('%Y-%m-%d')) 
        name = "%s-%s-%s.wav" % (self.deployment.owner.code, 
            self.deployment.site.code, 
            isotime(self.datetime), 
            )
        return os.path.join(settings.RECORDINGS_ROOT, 
            owner_dir,
            deployment_dir,
            name)

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


    def get_audio(self, offset=0, duration=0, max_framerate=settings.MAX_FRAMERATE):
        return wavy.get_audio(self.path, offset=offset, duration=duration, max_framerate=max_framerate)

class SonogramTransform(models.Model):
    n_fft = models.FloatField()
    framerate = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    dpi = models.FloatField()
    min_freq = models.FloatField()
    max_freq = models.FloatField()
    duration = models.FloatField()
    top_px = models.FloatField()
    bottom_px = models.FloatField()
    left_px = models.FloatField()
    right_px = models.FloatField()

    def pixel_to_physical(self, x, y):
        time = (x - self.left_px)/float(self.right_px - self.left_px)*self.duration
        frequency = (self.height - y - self.bottom_px)/float(self.top_px - self.bottom_px)*(self.max_freq - self.min_freq) + self.min_freq
        return time, frequency

    def physical_to_pixel(self, time, frequency):
        x = time/float(self.duration)*(self.right_px - self.left_px) + self.left_px
        y = self.height - (frequency - self.min_freq)/float(self.max_freq - self.min_freq)*(self.top_px - self.bottom_px) - self.bottom_px
        return x, y


class Snippet(models.Model):
    recording = models.ForeignKey(Recording, related_name='snippets')
    offset = models.FloatField() #seconds
    duration = models.FloatField()
    soundcloud = models.IntegerField(null=True, blank=True)
    fans = models.ManyToManyField(User, related_name='favourites', null=True, blank=True)

    class Meta:
        unique_together = (('recording', 'offset', 'duration'),)

    def __unicode__(self):
        return snippet_name(self)

    def get_audio(self, max_framerate=settings.MAX_FRAMERATE):
        try:
            print 'Getting audio locally'
            return wavy.get_audio(self.get_soundfile_name(), max_framerate=max_framerate)
        except (ValueError, SuspiciousOperation, AttributeError, IOError):
            print 'Getting audio remotely'
            return self.recording.get_audio(self.offset, self.duration, max_framerate=max_framerate)

    def save_sonogram(self, replace=False, n_fft=settings.N_FFT, \
        min_freq=settings.MIN_FREQ, \
        max_freq=settings.MAX_FREQ, \
        dpi=100,
        width=1000,
        height=350,
        max_framerate=settings.MAX_FRAMERATE):
        filename = self.get_sonogram_name()
        name = os.path.join(settings.SONOGRAM_DIR, filename)
        path = os.path.join(settings.MEDIA_ROOT, name)
        try:
            if not os.path.exists(path):
                replace = True
        except (ValueError, SuspiciousOperation, AttributeError):
            replace = True
        if replace:
            audio, framerate =  self.get_audio(max_framerate=max_framerate)
            Pxx, freqs, bins, im  = specgram(
                audio,
                NFFT=n_fft, 
                Fs=framerate
            )
            f = where(logical_and(freqs > min_freq, freqs <= max_freq))[0]
            Pxx[where(Pxx > percentile(Pxx[f].flatten(), 99.99))] =  percentile(Pxx[f].flatten(), 99.99)
            Pxx[where(Pxx < percentile(Pxx[f].flatten(), 0.01))] =  percentile(Pxx[f].flatten(), 0.01)
            clf()
            fig = figure(figsize=(float(width)/dpi, float(height)/dpi), dpi=dpi)
            imshow(flipud(10*log10(Pxx[f,])), 
                extent=(bins[0], bins[-1], freqs[f][0], freqs[f][-1]), 
                aspect='auto', 
                cmap=cm.gray )
            gca().set_ylabel('Frequency (Hz)')
            gca().set_xlabel('Time (s)')
            axis_pixels = gca().transData.transform(np.array((gca().get_xlim(), gca().get_ylim())).T)
            st, created = SonogramTransform.objects.get_or_create(
                n_fft=n_fft,
                framerate=framerate,
                min_freq=min_freq, 
                max_freq=max_freq,
                duration=self.duration,
                width=width,
                height=height,
                dpi=dpi,
                top_px=max(axis_pixels[:,1]),
                bottom_px=min(axis_pixels[:,1]),
                left_px=min(axis_pixels[:,0]), 
                right_px=max(axis_pixels[:,0]),
                )
            savefig(open(path, 'wb'), format='jpg', dpi=dpi)
            sonogram, created = Sonogram.objects.get_or_create(
                snippet = self,
                transform = st,
                path = name)
            close()

    def save_soundfile(self, replace=False):
        filename = self.get_soundfile_name()
        name = os.path.join(settings.SNIPPET_DIR, filename)
        path = os.path.join(settings.MEDIA_ROOT, name)
        try:
            if not os.path.exists(path):
                replace = True
        except (ValueError, SuspiciousOperation, AttributeError):
            replace = True
        if replace:
            wav_file = open(path, 'w')
            wavy.slice_wave(self.recording.path, wav_file, self.offset, self.duration)
            wav_file.close()
        return filename

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

class Sonogram(models.Model):
    snippet = models.ForeignKey(Snippet)
    transform = models.ForeignKey(SonogramTransform)
    path = models.TextField()

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

class Tag(UniqueSlugMixin, models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.TextField()
    datetime = models.DateTimeField(auto_now=True)
    #TODO: Add in a link to species
    #TODO: Rename the 'no-kiwis' tag to 'none'
    #TODO: Drop the 'interesting' tag (we will stick with the favourites for that)


    def __unicode__(self):
        return '%s' % (self.code)

class Analysis(SlugMixin, models.Model):
    name = models.TextField()
    code = models.SlugField(max_length=64, unique=True)
    description = models.TextField(default="")
    datetime = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    snippets = models.ManyToManyField(Snippet, through='AnalysisSet', related_name="analyses")
    user = models.ForeignKey(User, related_name="analyses")

    class Meta:
        unique_together = (('user', 'code'),)

    def __unicode__(self):
        return '%s' % (self.name)

class AnalysisSet(models.Model):
    analysis = models.ForeignKey(Analysis, related_name="sets")
    snippet = models.ForeignKey(Snippet, related_name="sets")
    selection_method = models.TextField(default="")
    datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('analysis', 'snippet'),)

class Identification(models.Model):
    user = models.ForeignKey(User, related_name="identifications")
    analysisset = models.ForeignKey(AnalysisSet, related_name="identifications")
    datetime = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="identifications") 
    tag_set = models.ManyToManyField(Tag) 
    comment = models.TextField(default="")

    class Meta:
        unique_together = (('analysisset', 'user'),)

class CallLabel(models.Model):
    code = models.TextField(unique=True)
    user = models.ForeignKey(User, related_name="call_labels")
    analysisset = models.ForeignKey(AnalysisSet, related_name="call_labels")
    datetime = models.DateTimeField(auto_now=True)
    tag = models.ForeignKey(Tag, related_name="call_labels") 
    tag_set = models.ManyToManyField(Tag)
    start_time = models.FloatField()
    end_time = models.FloatField()
    low_frequency = models.FloatField()
    high_frequency = models.FloatField()



