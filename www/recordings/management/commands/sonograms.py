import os
from datetime import datetime
from pylab import clf, specgram, savefig
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.images import ImageFile

from recordings.models import Snippet

class Command(BaseCommand):
    def handle(self, *args, **options):
        snippets = Snippet.objects.filter(sonogram='')
        for snippet in snippets:
            try:
                snippet.save_sonogram()
            except:
                #Logging goes here
                print '%s: %s' % (snippet, 'Error generating sonogram')
                pass

        
