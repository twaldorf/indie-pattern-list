import json
from pymongo import MongoClient

# env = os.environ.get('FLASK_ENV')

# Extract data from source
file_path = './mnm_all_ai_url_imageids.json'

patterns = []

with open(file_path) as file:
  data = json.load(file)
  patterns = data
    

# Connect with db
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['patternlistdev']
collection = db['patterns']

# res = collection.delete_many({})
# print(res)

# res = collection.update_many(
#   {}, { "$rename": { "price": "Cost", "designer": "Designer", "fabric_req": "Fabrics" } }
# )

for pattern, value in patterns.items():
  res = collection.insert_one(value)
  print(res)

# for pattern, value in patterns.items():
  # collection.insert_one(value)
  # value.fabric_req = value.fabric_req.fabric_req
  # print(value)
