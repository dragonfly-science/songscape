import csv, os
import hashlib
import random

from django.core.management.base import BaseCommand
from www.recordings.models import Snippet, Recording

import wavy
BASE_DIR = 'www/media/snippets'
class Command(BaseCommand):
    def handle(self, *args, **options):
        reader = csv.reader(open('/home/jasonhideki/songscape/www/media/snippets/snippets.csv'))
	#remove header row	
	reader.next()
	#make a list of all the unique recording paths that don't have serial number 000000       
	Recordings = []
	for row in reader:
	    if row[0] not in Recordings: #and row[0][16:22] != '000000':
		Recordings.append(row[0])
	#for every unique recording, pick 5 random snippet rows
	random_rows = []
	for i in range(len(Recordings)):
	    random_numbers = []
	    while len(random_numbers) < 5:
		if i == 0:
		    random_number = random.randrange(0,60,1)
		elif i >= 0:
		    random_number = random.randrange(1+i*60,60+i*60,1)
		if random_number not in random_numbers:
	            random_numbers.append(random_number)
	    	print random_numbers
	    random_rows.extend(random_numbers)
	reader = csv.reader(open('/home/jasonhideki/songscape/www/media/snippets/snippets.csv'))
	reader.next()
	writer = open("output.csv", 'wb')
	writer = csv.writer(writer, delimiter = ',')
	for i, row in enumerate(reader):
    	    if i in random_rows:
        	#print("This is the line.")
        	#print(row)
		writer.writerow(row)
'''
	#extract snippets based on output.csv
        reader = csv.reader(open('/home/jasonhideki/songscape/output.csv'))
        for i, row in enumerate(reader):
            if i:
                try:   
                    path = row[0]
                    offset = float(row[1])
                    duration = float(row[2])
                    md5 = hashlib.md5(open(path).read()).hexdigest()
                    print i, md5, path
		    #changed get criteria to path because weather test 000000 files have the same md5 as their non-000000 counterparts
		    #recording = Recording.objects.get(path = path)
                    recording = Recording.objects.get(md5 = md5)
                    snippet = Snippet.objects.get(recording=recording, offset=offset, duration=duration)
                    wavy.slice_wave(path, os.path.join(BASE_DIR, snippet.get_soundfile_name()), offset, duration, 8000)
                except Recording.DoesNotExist:
                    print "Can't find the recording on row %s at path %s" % (i, path)
                except:
                    print 'Something went wrong on row %s with recording %s' % (i, path)
                    raise
'''
            



	

