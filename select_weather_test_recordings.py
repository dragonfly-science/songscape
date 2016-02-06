import shutil
import os
import panda as pd
#for explanation of panda see http://stackoverflow.com/questions/16503560/read-specific-columns-from-csv-file-with-python-csv

#get the filenames you want to copy out from a csv file
df = pd.read_csv(csv_file) #change csv_file to match the path of the file you want to read from
saved_column = df.filestring #you can also use df['column_name']

#copy and move recordings to external drive
source = os.listdir("/tmp/") #change this to match the solardrive directory or wherever you'd like to copy files from
destination = "/tmp/newfolder/" #change this to match the path of the drive you'd like to copy to
for files in source:
    if files == saved_column:
        shutil.copy(files,destination)
