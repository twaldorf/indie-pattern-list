import json
from pymongo import MongoClient

def setup():
  # connect to the db
  client = MongoClient('mongodb://127.0.0.1:27017')
  collection = client['patternlistdev']['patterns']
  return collection