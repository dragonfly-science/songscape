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

from www.recordings.models import Deployment, Recording, Snippet

BASE_PATH = 'www/recordings/recordings'
MIN_FILE_SIZE = 1000
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    filename='songscape-load-recordings.log')

class RecorderSiteError(Exception):
    pass

def get_starttime(filename, count=0):
    """returns the start time, by parsing the filename of a WAV file from the DOC recorders"""
    filename_timestamp = filename[0:12]
    logging.debug('still good')
    timestamp = mktime(strptime(filename_timestamp, "%d%m%y%H%M%S"))
    #timestamp = mktime(strptime(filename, "%d%m%y_%H%M%S.wav"))
    logging.debug('still good2')
    timestamp += count*60
    return  pytz.utc.localize(datetime.fromtimestamp(timestamp))

def get_md5(path):
    hasher = hashlib.md5()
    try:
        hasher.update(open(path, 'rb').read())
    except IOError:
        logging.error('unable to read recording: %s', path)
    return hasher.hexdigest()

'''
def save_canonical(recording):
    logging.debug('copy to canonical location: %s', recording.path)
    if os.path.exists(recording.path):
        new_path = recording.get_canonical_path()
        logging.debug('canonical location is: %s', new_path)      
	if recording.path == new_path:
            return 
        if os.path.exists(new_path) and recording.md5 == get_md5(new_path):
            recording.path = new_path
            recording.save()
            logging.debug('updated recording to use  canonical location: %s', new_path)
            return
   	try:
            try:
                os.makedirs(os.path.split(new_path)[0])
	    except TypeError:
		pass
            except OSError:
                pass
            shutil.copyfile(recording.path, new_path)
            logging.info('copied file to canonical location: %s', new_path)
            recording.path = new_path
            recording.save()
        except (IOError, OSError):
            logging.error('unable to copy to canonical location: %s', recording.path)
    else:
        logging.error('no file at expected path: %s', recording.path)
'''

def get_recorder_site(filename, count=0):
   recorder = filename[16:22]
   site = filename[12:16]
   if recorder and site:
	return (recorder, site)
   else:
	raise RecorderSiteError

'''
def get_recorder_site(path, count=0):
    # check for Susan's new paths
    m = re.match(".*/data_by_location/(?P<recorder>KR[A-Z0-9]+)_.*", path)
    if m:
        return m.groups()[0].upper(), None
    m = re.match(".*/data_by_location/(?P<site>[a-zA-Z0-9]+)_.*", path)
    if m:
        return None, m.groups()[0].upper()
    # First check for an Innes style path
    m = re.match(".*/MIC_(?P<recorder>KR\w+).*/LOCATION_\d*_(?P<site>\w+)/.*", path)
    if m:
        return [x.upper() for x in m.groups()]
    # check for recorder only paths
    m = re.match(".*/(?P<recorder>kr\d+)[abAB]?/.*wav", path)
    if m:
        return m.groups()[0].upper(), None
    raise RecorderSiteError
'''

class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.debug("started")
        for root, dirs, files in os.walk("/home/jasonhideki/songscape/www/recordings/recordings"):
            for f in files:
                if f.endswith('.wav'):
                    # First check to see if it exists
                    path = os.path.join(root, f)
                    if os.path.getsize(path) < MIN_FILE_SIZE:
                        logging.info('small file ignored: %s', path)
                        continue
		    md5 = get_md5(path)
                    '''
		    try:                      
			recording = Recording.objects.get(md5=md5)
                        logging.info('recording with same MD5 already in database: %s', path)
                        save_canonical(recording)
                        #continue
                    except Recording.DoesNotExist:
                        logging.debug('recording not already in database: %s', path)
                        pass
		    '''
		    # Now get the file path
		    try: 
			starttime = get_starttime(f)
                    except ValueError:
                        logging.error('unable to extract date and time from filename: %s', path)
                    try:
			recorder_code, site_code = get_recorder_site(f)
			logging.debug('recorder %s and site %s: %s', recorder_code, site_code, f)
		    
		    #try:
                    #    recorder_code, site_code = get_recorder_site(path)
                    #    logging.debug('recorder %s and site %s: %s', recorder_code, site_code, path)
                        if site_code and recorder_code:
                            deployment = Deployment.objects.get(recorder__code=recorder_code, 
                                site__code=site_code,
                                start__lt=starttime, 
                                end__gt=starttime)
                        elif recorder_code:
                            deployment = Deployment.objects.get(recorder__code=recorder_code, 
                                start__lt=starttime, 
                                end__gt=starttime)
                        elif site_code:
                            deployment = Deployment.objects.get(site__code=site_code, 
                                start__lt=starttime, 
                                end__gt=starttime)
                        else:
                            logging.error('no site or recorder identified in path: %s', path)
                            continue
                        logging.debug('found the deployment: %s', deployment)
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
                        logging.info('added recording to database: %s', path)
                        #save_canonical(recording)
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
                    except:
                        logging.error('Hmmm. Something weird happened with this file: %s', path)
                                
