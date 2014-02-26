import csv, os
import hashlib

from django.core.management.base import BaseCommand
from www.recordings.models import Snippet, Recording

import wavy
BASE_DIR = '/kiwi/identifications/rfpt/snippets'
class Command(BaseCommand):
    def handle(self, *args, **options):
        reader = csv.reader(open(args[0]))
        for i, row in enumerate(reader):
            if i:
                try:   
                    path = row[0]
                    offset = float(row[1])
                    duration = float(row[2])
                    md5 = hashlib.md5(open(path).read()).hexdigest()
                    print i, md5, path
                    recording = Recording.objects.get(md5 = md5)
                    snippet = Snippet.objects.get(recording=recording, offset=offset, duration=duration)
                    wavy.slice_wave(path, os.path.join(BASE_DIR, snippet.get_soundfile_name()), offset, duration, 8000)
                except Recording.DoesNotExist:
                    print "Can't find the recording on row %s at path %s" % (i, path)
                except:
                    print 'Something went wrong on row %s with recording %s' % (i, path)
                    raise

            

            
            
            
