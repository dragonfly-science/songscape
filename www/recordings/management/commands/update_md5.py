import logging

from django.core.management.base import BaseCommand

from www.recordings.models import Recording


class Command(BaseCommand):
    def handle(self, **options):
        for recording in Recording.objects.all():
            try:
                recording.md5 = recording.get_hash()
                recording.save()
            except:
                logging.error('unable to update recording %s', recording)
