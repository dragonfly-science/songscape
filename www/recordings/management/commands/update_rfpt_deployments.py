import csv
from datetime import datetime, timedelta
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from www.recordings.models import Organisation, Site, Recorder, Deployment

DIR = 'fixtures'

class Command(BaseCommand):
    def handle(self, **options):
        rfpt_org = Organisation.objects.get(code='RFPT')
        deployments = csv.DictReader(open(os.path.join(DIR, 'Deployments.csv')))
        count_found = 0
        count_new = 0
        for row in deployments:
            try:
                site = Site.objects.get(code=row['Site'])
            except Site.DoesNotExist:
                site = Site(code=row['Site'], organisation=rfpt_org)
                site.save()
            recorder = Recorder.objects.get(code=row['Recorder'].strip())
            start = datetime.strptime(row['Start'], '%d/%m/%Y') 
            if row['End'].strip():
                end = datetime.strptime(row['End'], '%d/%m/%Y')
            else:
                end = None
            try:
                o = Deployment.objects.get(site=site, 
                    recorder=recorder, 
                    start__gt=start - timedelta(days=1), 
                    end__lt=end + timedelta(days=1), 
                    owner=rfpt_org)
                count_found += 1
            except Deployment.DoesNotExist:
                count_new += 1
                o = Deployment(site=site, 
                    recorder=recorder, 
                    start=start + timedelta(hours=12), 
                    end=end + timedelta(hours=12), 
                    owner=rfpt_org)
                o.save()
                print "New deployment %s: %s, %s, %s" % (count_new, site, recorder, start)
                pass
        print "%s existing deployments; %s new deployments" % (count_found, count_new)

