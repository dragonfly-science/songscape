from django.core.management.base import BaseCommand

from pymongo import MongoClient
from gridfs import GridFS

import os

from www.recordings.models import Recording, Snippet

class Command(BaseCommand):
    def handle(self, *args, **options):
        recordings = Recording.objects.all()
        mongo = MongoClient()
        fs = GridFS(mongo.songscape, collection='recordings')
        for r in recordings:
            if fs.exists(md5=r.md5):
                print "skipping", r.path
                continue
            _, filename = os.path.split(r.path)    
            gridfile = fs.new_file(filename=filename, 
                                   site=str(r.deployment.site),
                                   recorder=str(r.deployment.recorder),
                                   owner=str(r.deployment.owner),
                                   datetime=r.datetime,
                                   content_type='audio/wav')
            gridfile.write(open(r.path, 'rb'))
            gridfile.close()
            print 'writing', r.path
