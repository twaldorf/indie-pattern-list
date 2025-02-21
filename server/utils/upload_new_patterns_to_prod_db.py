from pymongo import MongoClient
import json

pword = input('Prod password:')

local_client = MongoClient('mongodb://127.0.0.1:27017')
local_collection = local_client['patternlistdev']['patterns']

try:
  prod_client = MongoClient(f'mongodb+srv://twaldorf:{pword}@dps-cluster.3ialgeu.mongodb.net/?retryWrites=true&w=majority&appName=dps-cluster')
  prod_collection = prod_client['superpatternlist']['patterns']
except:
  print('Error connecting to prod_collection')

def sendbatchToProd():
  patterns = local_collection.find({})
  for pattern in patterns:
    exists = prod_collection.find_one({
      '$or': [
        {'title': pattern['title']},
        {'_id': pattern['_id']}
      ]
    })
    if not exists:
      prod_collection.insert_one(pattern)
    
sendbatchToProd()