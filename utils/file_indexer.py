import argparse

import pymongo
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument("-h", "--host", help="database host", default="localhost")	
parser.add_argument("-p", "--port", type=int, help="database port", default=27017)	

if __name__ == "__main__":
	args = arser.parse_args()
	
	client = MongoClient(args.host, args.port)	
	db = client.songscape
	collection = db.files








