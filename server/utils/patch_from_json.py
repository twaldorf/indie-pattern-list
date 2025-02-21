import json
from pymongo import MongoClient

# connect to the db
client = MongoClient('mongodb://127.0.0.1:27017')
collection = client['patternlistdev']['patterns']

file_path = './uploads/cc_patch.json'

with open(file_path) as file:
  data = json.load(file)
  patterns = data

# print(patterns)

for pattern in patterns:
  filter = { 'title': pattern['title'] }
  update = { '$set': pattern }
  res = collection.update_one(filter, update)
  print(res)