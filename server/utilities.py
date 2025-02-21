import csv
from pymongo import MongoClient

env = os.environ.get('FLASK_ENV')

# Extract data from source
if env == 'development':
  file_path = './db.csv'
elif env == 'production':
	file_path = '/lake/patterns.csv'

patterns = []

with open (file_path, newline='', encoding='utf-8') as pattern_source:
  csv_reader = csv.DictReader(pattern_source)
  for row in csv_reader:
				newrow = row
				for col in row:
					newrow[col] = newrow[col].split(',')
					newrow[col] = [entry.strip() for entry in newrow[col]]
				patterns.append(newrow)

# Connect with db
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['patternlistdev']
collection = db['patterns']

for pattern in patterns:
	collection.insert_one(pattern)

