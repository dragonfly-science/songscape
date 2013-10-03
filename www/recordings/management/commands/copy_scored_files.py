import os
import random
import shutil

from django.core.management.base import BaseCommand, CommandError

from www.recordings.models import Snippet, Analysis, AnalysisSet, Detector, Score, Identification, Tag

class Command(BaseCommand):
    def handle(self, *args, **options):
        mk = Tag.objects.get(code='male-kiwi')
        fk = Tag.objects.get(code='female-kiwi')
        nk = Tag.objects.get(code='no-kiwis')
        analysis = Analysis.objects.get(code='rimutaka-kiwi')
        
        ids = {}
        ids['male'] = Snippet.objects.filter(identifications__in = Identification.objects.filter(true_tags = mk))
        ids['female'] =  Snippet.objects.filter(identifications__in = Identification.objects.filter(true_tags = fk))
        ids['no'] = Snippet.objects.filter(identifications__in = Identification.objects.filter(true_tags = nk))
        
        try:
            os.mkdir('/kiwi/identified')
            os.mkdir('/kiwi/identified/male-kiwi')
            os.mkdir('/kiwi/identified/female-kiwi')
            os.mkdir('/kiwi/identified/no-kiwi')
        except OSError:
            pass

        for key, snips in  ids.items():
            count = 0
            for snip in snips:
                try:
                    snip.save_soundfile()
                    shutil.copyfile(snip.soundfile.path, '/kiwi/identified/%s-kiwi/%s'%(key, os.path.split(snip.soundfile.name)[1]))
                    count += 1
                    print key, count
                except KeyError:
                    raise
#                except:
#                    pass
