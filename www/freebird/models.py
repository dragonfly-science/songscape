
from www.recordings.models import Tag

class Species(models.Model):
    name = models.TextField()
    code = models.IntegerField()
    bioweb_code = models.IntegerField()
    filename = models.TextField()
    tag = models.ManyToManyField(Tag, related_name='freebird_species')





