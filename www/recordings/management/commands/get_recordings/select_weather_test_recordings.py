import shutil
import os
import csv
from collections import defaultdict

#get the filenames out of the csv file
columns = defaultdict(list) # each value in each column is appended to a list

with open('/home/jasonhideki/songscape/weather_test_tester.csv') as f:
    reader = csv.DictReader(f) # read rows into a dictionary format
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        for (k,v) in row.items(): # go over each column name and value 
            columns[k].append(v) # append the value into the appropriate list
                                 # based on column name k

#print(columns['filestring']) #to test the above code
saved_column = columns['filestring']
#for info on how the above section works see http://stackoverflow.com/questions/16503560/read-specific-columns-from-csv-file-with-python-csv

#Select only morning recordings
#morn_recordings = []
#for r in recording_datetime:
#	recording_hour = r.hour
#	if recordings_start < 11 and recordings_start > 06:		
#	morn_recordings = morn_recordings.append(recording_file)

#copy and move recordings to external drive if they are morning recordings
r_directory = "/home/jasonhideki/songscape/www/recordings/recordings/"
source = os.listdir(r_directory) #change this to match the solardrive directory or wherever you'd like to copy files from
#print source #to test the above code
destination = "/home/jasonhideki/songscape/" #change this to match the path of the drive you'd like to copy to
for f in source:
    if f[6:7] == '07':
	print f
    #if f in saved_column: #and f[6:7] == '07':
    #    shutil.copy(r_directory + f,destination)


