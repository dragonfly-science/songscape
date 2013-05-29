
from django.core.management.base import BaseCommand
from django.conf import settings

from pymongo import MongoClient
from gridfs import GridFS

import os

from recordings.models import Snippet

class Command(BaseCommand):
    def handle(self, *args, **options):
        snippets = Snippet.objects.exclude(sonogram=None)
        mongo = MongoClient()
        fs = GridFS(mongo.songscape, collection='snippets')
        for s in snippets:
            _, sonogramname = os.path.split(s.sonogram.name)
            if fs.exists(filename=sonogramname):
                print "skipping", sonogramname
                continue
            gridfile = fs.new_file(filename=sonogramname,
                                   content_type='image/png')
            base = '/home/edward/dragonfly/songscape/www/media/sonograms/'
            path = base + sonogramname 
            gridfile.write(open(path, 'rb'))
            gridfile.close()
            print 'writing', sonogramname
