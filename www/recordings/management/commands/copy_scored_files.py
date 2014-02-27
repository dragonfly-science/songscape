import os
import random
import shutil
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from www.recordings.models import Identification, CallLabel

# Normalise the call time
def standardize(t):
    return min(60, max(float(t), 0))

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--user',
            dest='user',
            help='restrict to analysis by this user'),
        make_option("--no-snippets",
            action="store_false", 
            dest="get_snippets", 
            default=True,
            help="Get the snippets"),
        )


    def handle(self, *args, **options):
        analysis = args[0]
        user = options.get('user', '')
        tags = args[1:]
        print tags
        identifications = Identification.objects.filter(analysisset__analysis__code=analysis)
        if user:
            identifications = identifications.filter(user__username=user)

        call_labels = CallLabel.objects.filter(analysisset__analysis__code=analysis)
        if user:
            call_labels = call_labels.filter(user__username=user)

        #FIrstly, ensure that all the snippets are present
        if options['get_snippets']:
            print "Creating snippets"
            path = '/kiwi/identified/rfpt/snippets'
            for identification in identifications:
                name = identification.analysisset.snippet.get_soundfile_name()
                if not os.path.exists(os.path.join(path, name)):
                    identification.analysisset.snippet.save_soundfile(replace=False, path=path, max_framerate=8000)
    
        #process the calls
        calls = {}
        for identification in identifications:
            calls[identification.analysisset.snippet.get_soundfile_name()] = []

        for call in call_labels:
            if call.tag.code in tags:
                calls[call.analysisset.snippet.get_soundfile_name()].append((standardize(call.start_time), standardize(call.end_time)))

        # Now output the data
        output = open('call-labels-%s.txt' % ('-'.join(tags)), 'w')
        for soundfile, labels in calls.items():
            labels.sort()
            stack = []
            for i, label in enumerate(labels):
                if i == 0:
                    stack.append(label[0])
                    stack.append(label[1])
                if i > 0:
                    if label[0] > stack[-1]:
                        stack.append(label[0])
                        stack.append(label[1])
                    else:
                        stack.pop()
                        stack.append(label[1])
            if not sorted(stack) == stack:
                print stack
                raise ValueError, 'call times should be sorted'
            output.write(soundfile + ' ')
            output.write(' '.join([str(s) for s in stack]))
            output.write('\n')
        output.close()
        


        








