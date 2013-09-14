#! /usr/bin/python
'''
This script is used for storing files in a MongoDB GridFS store. The files are expected to be
read only, and are identified by their MD5 sum. The idea is that they may be transferred from
standard file systems, or portable drives, into the GridFS store, where they are available
to users over the network.

Example usage:
python file_indexer.py /myfiles -d audiofiles -f "*.wav"


'''

import argparse
import fnmatch
import hashlib
import time
import mimetypes
import os
import socket
import logging

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
parser.add_argument("-m", "--mimetype", help="Specify the mimetype of the files", default="")    
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")    

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG if args.verbose else logging.INFO
    )
    client = MongoClient(args.host, args.port)    
    db = client[args.database]
    fs = GridFS(db, collection=args.collection)
    server = args.server or socket.gethostname()
    write_count = 0
    item_count = 0
    error_count = 0
    start = time.time()
    for root, directories, files in os.walk(args.directory):
        for item in fnmatch.filter(files, args.filter):
            item_count += 1
            path = os.path.abspath(os.path.join(root, item))
            full_path = '%s:%s' % (server, path)
            try:
                # Get the MD5 hash of the file
                handle = open(path, 'rb')
                digest = hashlib.md5()
                for block in iter(lambda: handle.read(1024*1024), ""):
                    digest.update(block)
                handle.seek(0)
                md5 = digest.hexdigest()
            except IOError:
                logging.error('unable to read file %s', full_path)
                error_count += 1
                continue
            # Add the file to MongoDB if it isn't already added
            if fs.exists(md5=md5):
                db['%s.files' % args.collection].update({'md5': md5}, 
                    {'$addToSet': {'aliases': full_path}})
                logging.debug('Updated file %s', full_path)
            else:
                kwargs = {'filename': item, 'aliases': [full_path]}
                mimetype = args.mimetype or \
                    mimetypes.guess_type(item, strict=False)[0]
                if mimetype:
                    kwargs['contentType'] = mimetype
                try:
                    _id = fs.put(handle, **kwargs)
                    write_count += 1
                    logging.debug('Wrote file %s', full_path)
                except IOError:
                    logging.error('unable to write file %s', full_path)
                    error_count += 1
                    continue
    logging.info('%s files processed', item_count)
    logging.info('%s files written to MongoDB', write_count)
    logging.info('%s errors', error_count)
    logging.info('processing took %s s', int(time.time() - start))
                    









