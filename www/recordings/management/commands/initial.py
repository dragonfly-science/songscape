import csv
from datetime import datetime
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from recordings.models import Organisation, Site, Recorder, Deployment

DIR = 'fixtures'

class Command(BaseCommand):
    def handle(self, **options):
        organisation = csv.DictReader(open(os.path.join(DIR, 'Organisations.csv')))
        for row in organisation:
            o = Organisation(code=row['Code'], name=row['Name'])
            o.save()

        sites = csv.DictReader(open(os.path.join(DIR, 'Sites.csv')))
        for row in sites:
            if not row['Latitude'].strip():
                row['Latitude'] = None
            if not row['Longitude'].strip():
                row['Longitude'] = None
            o = Site(code=row['Code'], latitude=row['Latitude'], longitude=row['Longitude'], comments=row['Comments'])
            o.save()

        recorders = csv.DictReader(open(os.path.join(DIR, 'Recorders.csv')))
        for row in recorders:
            org = Organisation.objects.get(code=row['Owner'])
            o = Recorder(code=row['Code'], organisation=org)
            o.save()
        
        deployments = csv.DictReader(open(os.path.join(DIR, 'Deployments.csv')))
        for row in deployments:
            site = Site.objects.get(code=row['Site'])
            recorder = Recorder.objects.get(code=row['Recorder'].strip())
            if not row['Deploy_time']:
                row['Deploy_time'] = '00:00:00'
            if not row['Recovery_time']:
                row['Recovery_time'] = '00:00:00'
            start = datetime.strptime(row['Deploy_date'] + ' ' + row['Deploy_time'], '%d/%m/%Y %H:%M:%S') 
            if row['Recovery_date'].strip():
                end = datetime.strptime(row['Recovery_date'] + ' ' + row['Recovery_time'], '%d/%m/%Y %H:%M:%S')
            else:
                end = None
            o = Deployment(site=site, recorder=recorder, start=start, end=end, comments=row['Comments'])
            o.save()

