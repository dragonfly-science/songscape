import argparse
import os
import hashlib
import fnmatch
import socket

import pymongo
from pymongo import MongoClient
from gridfs import GridFS

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="start directory", default=".")    
parser.add_argument("-H", "--host", help="Mongo database host", default="localhost")    
parser.add_argument("-P", "--port", type=int, help="Mongo database port", default=27017)    
parser.add_argument("-f", "--filter", help="file pattern", default="*")    
parser.add_argument("-s", "--server", help="server name", default="")    
parser.add_argument("-c", "--collection", help="Mongo collection name", default="fs")    
parser.add_argument("-d", "--database", help="Mongo database name", default="test")    

if __name__ == "__main__":
    args = parser.parse_args()
    
    client = MongoClient(args.host, args.port)    
    db = client[args.database]
    fs = GridFS(db, collection=args.collection)

    server = args.server or socket.gethostname()
    for root, directories, files in os.walk(args.directory):
        for item in fnmatch.filter(files, args.filter):
            path = os.path.abspath(os.path.join(root, item))
            handle = open(path, 'rb')
            digest = hashlib.md5()
            for block in iter(lambda: handle.read(1024*1024), ""):
                digest.update(block)
            handle.seek(0)
            md5 = digest.hexdigest()
            if not fs.exists(md5=md5):
                print 'writing', path
                fs.put(handle)
            db['kokako.files'].update({'md5': md5}, 
                {'$addToSet': {'aliases': '%s:%s' % (server, path)}},
                upsert=True)
            









