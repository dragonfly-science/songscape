import argparse
import os
import hashlib
import fnmatch
import socket

import pymongo
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="start directory", default=".")	
parser.add_argument("-H", "--host", help="database host", default="localhost")	
parser.add_argument("-P", "--port", type=int, help="database port", default=27017)	
parser.add_argument("-f", "--filter", help="file pattern", default="*")	
parser.add_argument("-s", "--server", help="server name", default="")	

if __name__ == "__main__":
	args = parser.parse_args()
	
	client = MongoClient(args.host, args.port)	
	db = client.test
	collection = db.files

print args.filter
server = args.server or socket.gethostname()
for root, directories, files in os.walk(args.directory):
    for item in fnmatch.filter(files, args.filter):
        path = os.path.abspath(os.path.join(root, item))
        handle = open(path, 'rb')
        digest = hashlib.md5()
        for block in iter(lambda: handle.read(1024*1024), ""):
            digest.update(block)
        collection.update({'md5': digest.hexdigest()}, 
            {'$addToSet': {'paths': '%s:%s' % (server, path)}},
            upsert=True)
            









