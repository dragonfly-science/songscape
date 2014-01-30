from datetime import datetime
import os
import shutil
import wave
import hashlib
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import utc
import pytz

from www.recordings.models import Deployment, Recording, Snippet
from www.recordings.templatetags.recording_filters import isotime

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    filename='songscape-fix-recording-times.log')

class Command(BaseCommand):
    def handle(self, *args, **options):
        # First, fix the deployment times
        logging.info("fix deployment times")
#        for d in Deployment.objects.all():
#            logging.info(d)
#            d.start = pytz.timezone(d.start_timezone).localize(d.start.replace(tzinfo=None)).astimezone(utc)
#            d.end = pytz.timezone(d.start_timezone).localize(d.end.replace(tzinfo=None)).astimezone(utc)
#            d.save()
#            print d.start, d.end
        already = 0
        moved = 0
        for r in Recording.objects.all():
            if 'Z' in r.path:
                already += 1
                logging.info('%s. Already moved %s' % (already, r))
                continue
            # Second, check that the files are where they are expected to be
            if not r.verify_hash():
                msg = "Something wrong wth file %s" % r.path
                logging.error(msg)
            else:
                moved += 1
                logging.info('%s. Moving %s' % (moved, r))
                # Third, update the datetime in the database
                r.datetime = pytz.timezone(r.deployment.start_timezone).localize(r.datetime.replace(tzinfo=None)).astimezone(utc)
                r.save()
                # Fourth, move the file
                directory, name = os.path.split(r.path)
                new_name = "%s-%s-%s.wav" % (r.deployment.owner.code, 
                r.deployment.site.code, 
                isotime(r.datetime))
                new_path = os.path.join(directory, new_name)
                os.rename(r.path, new_path)
                #Fively, update the path to match
                r.path = new_path
                r.save()

                if not r.verify_hash():
                    msg = "Oops. Something wrong wth file %s" % r.path
                    logging.error(msg)
                    raise ValueError, msg
                                
