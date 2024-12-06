import json
from pymongo import MongoClient

def load_json(file_path=None, collection=None):
  # env = os.environ.get('FLASK_ENV')

  # Extract data from source
  if not file_path:
    file_path = './uploads/'

  filename = input('Filename:')
  file_path = file_path + filename

  patterns = []

  with open(file_path) as file:
    data = json.load(file)
    patterns = data
      
  # Connect with db
  client = MongoClient('mongodb://127.0.0.1:27017')
  db = client['patternlistdev']

  if collection is None:
    collection = db['patterns']

  # res = collection.delete_many({})
  # print(res)

  # res = collection.update_many(
  #   {}, { "$rename": { "price": "Cost", "designer": "Designer", "fabric_req": "Fabrics" } }
  # )
  print('Inserting into collection')

  for pattern in patterns:
    existing = collection.find({'title': pattern['title']})
    if len(list(existing)) > 0:
      for ep in existing:
        for attribute in pattern:
          ep[attribute] = pattern[attribute]
        update = { '$set': ep }
        res = collection.update_one({'_id': ep['_id']}, update)
        print(ep['title'])
        print(res)
    else:
      res = collection.insert_one(pattern)
      print(pattern['title'])
      print(res)


  # for pattern, value in patterns.items():
    # collection.insert_one(value)
    # value.fabric_req = value.fabric_req.fabric_req
    # print(value)

load_json()