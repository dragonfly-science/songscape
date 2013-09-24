import sys
from django.core.management.base import BaseCommand

from www.recordings.models import Snippet

class Command(BaseCommand):
    def handle(self, *args, **options):
        snippets = Snippet.objects.filter(sonogram='')
        for snippet in snippets:
            try:
                snippet.save_sonogram(replace=False)
                sys.stdout.write('\r%s' % snippet )
                sys.stdout.flush()
            except KeyboardInterrupt:
                break
            except:
                #Logging goes here
                print '%s: %s (%s)' % (snippet, 'Error generating sonogram', 
                    sys.exc_info()[0])
                pass
