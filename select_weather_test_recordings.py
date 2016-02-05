import shutil
import os
import panda as pd
#for explanation of panda see http://stackoverflow.com/questions/16503560/read-specific-columns-from-csv-file-with-python-csv

#get the filenames you want to copy out
df = pd.read_csv(csv_file)
saved_column = df.column_name #you can also use df['column_name']

#copy and move recordings to external drive
source = os.listdir("/tmp/")
destination = "/tmp/newfolder/"
for files in source:
    if files == saved_column:
        shutil.copy(files,destination)
