import sys
from django.core.management.base import BaseCommand

from www.recordings.models import AnalysisSet

class Command(BaseCommand):
    def handle(self, *args, **options):
        analysis_set = AnalysisSet.objects.all()
        for a in analysis_set:
            try:
                a.snippet.save_sonogram()
                sys.stdout.write('\r%s' % a.snippet )
                sys.stdout.flush()
            except KeyboardInterrupt:
                break
            except:
                #Logging goes here
                print '%s: %s (%s)' % (a.snippet, 'Error generating sonogram', 
                    sys.exc_info()[0])
                pass
