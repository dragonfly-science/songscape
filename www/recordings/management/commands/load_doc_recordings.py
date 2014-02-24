from datetime import datetime
import os, sys
import shutil
from time import time, strptime, strftime, mktime
import re
import wave
import hashlib
from contextlib import closing
import logging
import traceback
import pytz

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError

from www.recordings.models import Deployment, Recording, Snippet, Site, Organisation

BASE_PATH = '/kiwi/nocturnal-calls'
MIN_FILE_SIZE = 1000
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    filename='songscape-load-recordings.log')


def get_md5(path):
    hasher = hashlib.md5()
    try:
        hasher.update(open(path, 'rb').read())
    except IOError:
        logging.error('unable to read recording: %s', path)
    return hasher.hexdigest()

class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.debug("started")
        recordings = []
        for root, dirs, files in os.walk(args[0]):
            for f in files:
                if f.endswith('.wav'):
                    recordings.append((f, os.path.join(root, f)))
        recordings.sort()
        #First make the organisation
        try:
            doc = Organisation.objects.get(code='doc')
        except Organisation.DoesNotExist:
            doc = Organisation(code='doc', name='Department of Conservation')
            doc.save()
            logging.info('Made a new organisation: doc')
        #Now make the sites
        site_codes = set(['_'.join(f.split('_')[:2]) for (f, path) in recordings])
        for code in site_codes:
            try:
                Site.objects.get(code=code, organisation=doc)
            except Site.DoesNotExist:
                Site(code=code, organisation=doc).save()
                logging.info('Made a new site: %s' % code)
        #Now make the deployments
        tz = pytz.timezone('Etc/GMT-12')
        old_site = ''
        last_date = tz.localize(datetime.strptime('20000101', '%Y%m%d'))
        count = 0
        for f, path in recordings:
            count += 1
            if count > 200: break
            site_code = '_'.join(f.split('_')[:2])
            date = tz.localize(datetime.strptime(f.split('_')[2], '%y%m%d'))
            starttime = tz.localize(datetime.strptime('_'.join(f.split('_')[2:4]), '%y%m%d_%H%M%S.wav'))
            if site_code != old_site or (date - last_date).days > 1:
                old_site = site_code
                site = Site.objects.get(code=site_code, organisation=doc)
                deployment, created = Deployment.objects.get_or_create(site=site, owner=doc,
                        start=date, start_timezone='Pacific/Auckland')
                if created:
                    deployment.save()
                    logging.info('Made a new deployment: %s, %s' % (site, date))
            last_date = date
                    
            if os.path.getsize(path) < MIN_FILE_SIZE:
                logging.info('small file ignored: %s', path)
                continue
            md5 = get_md5(path)
            try:
                recording = Recording.objects.get(md5=md5)
                logging.info('recording with same MD5 already in database: %s', path)
                recording.path = path
                recording.save()
                continue
            except Recording.DoesNotExist:
                logging.debug('recording not already in database: %s', path)
                pass
            try:
                try:
                    Recording.objects.get(datetime=starttime, deployment=deployment)
                    logging.error('recording already exists with the same startime (%s) and deployment (%s): %s',
                        starttime, deployment, path)
                    continue
                except Recording.DoesNotExist:
                    pass
                recording = Recording(datetime=starttime, deployment=deployment, path=path)
                logging.debug('created the recording: %s', recording)
                recording.save()
                logging.debug('generate the snippets: %s', path)
                #Now generate the snippets
                if not recording.snippets.count():
                    try:
                        with closing(wave.open(path, 'r')) as w:
                            frames = w.getnframes()
                            rate = w.getframerate()
                            length = frames/float(rate)
                            snippet_length = 60
                            snippet_overlap = 0
                            snippet_minimum = 59.9
                            seconds = 0
                            while seconds + snippet_minimum < length: 
                                offset = max(seconds - snippet_overlap, 0)
                                duration = min(snippet_length + 2*snippet_overlap, length - offset)
                                Snippet(recording=recording, offset=offset, duration=duration).save()
                                seconds += snippet_length
                    except KeyboardInterrupt:
                        break
                    except:
                        logging.error('error extracting snippet: %s', path)
            except Deployment.DoesNotExist:
                logging.error('no matching deployment found: %s', path)
            except Deployment.MultipleObjectsReturned:
                logging.error('multiple matching deployment found: %s', path)
            except IntegrityError:
                logging.error('integrity error when trying to save file: %s', path)
            except wave.Error:
                logging.error("doesn't seem to be a WAV file: %s", path)
            except RecorderSiteError:
                logging.error('unable to extract recorder or site from path: %s', path)
            except KeyboardInterrupt:
                break
                                
