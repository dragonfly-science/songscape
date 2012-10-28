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

class Score(models.Model):
    datetime = models.DateTimeField()
    deployment = models.ForeignKey(Deployment)
    energy_index = models.FloatField()
    kiwi_index = models.FloatField()
    date_scored = models.DateTimeField(auto_now_add=True)
    filename = models.TextField()
    sonogram = models.ImageField(upload_to=settings.SONOGRAM_DIR, null=True, blank=True)
    kiwi = models.NullBooleanField(null=True, blank=True)


