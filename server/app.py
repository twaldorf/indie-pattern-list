from flask import Flask, jsonify, request
from flask_cors import CORS
import json, csv
from pymongo import MongoClient
from bson import ObjectId

csv_path = 'db.csv'

app = Flask(__name__)

origins = [
	"https://ips-client.vercel.app",
	"https://www.superpatternlist.com",
	"http://localhost:5173"
]

CORS(app, resources={r"/*": {"origins": origins}})

# connect to db
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['patternlistdev']
collection = db['patterns']

@app.route('/patterns', methods=['GET'])
def index():
		# paginate
		page_index = int(request.args.get('page', 1))
		page_size = int(request.args.get('page_length', 50))
		front = (page_index - 1) * page_size
		back = front + page_size

		patterns = get_patterns_from_db()[front : back]

		#sort 
		sortBy = request.args.get('SortBy')
		
		if sortBy == 'price':
			for row in patterns:
				if row['price'][0] != '':
					row['price'] = float( row['price'].replace("$", "") )
				else:
					row['price'] = 0.0
			if sortBy:
				patterns.sort(key=lambda x: x.get( sortBy, ''))

		return jsonify(patterns)

def prep_patterns(patterns):
	for pattern in patterns:
		pattern['_id'] = str(pattern['_id'])
	return patterns

def get_patterns_from_db():
	patterns = list(collection.find({}))
	for pattern in patterns:
		pattern['_id'] = str(pattern['_id'])
	
	return patterns


def read_csv(file_path):
	patterns = []

	with open(file_path, newline='', encoding='utf-8') as csvfile:
			csv_reader = csv.DictReader(csvfile)
			for row in csv_reader:
				newrow = row
				for col in row:
					newrow[col] = newrow[col].split(',')
					newrow[col] = [entry.strip() for entry in newrow[col]]
				patterns.append(newrow)

	return patterns
	
# @app.route('/patterns', methods=['GET'])
# def get_patterns():
# 	with open('db.json', 'r') as file:
# 		data = json.load(file)

# 	return jsonify(data)

# def get_pattern_by_image(image_name):
#     with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
#         csv_reader = csv.DictReader(csvfile)
#         for row in csv_reader:
#             if row['Image'] == image_name:
#                 return row

#     # If no matching row is found, return None
#     return None

def get_pattern_by_id(id):
	pattern = collection.find_one({'_id': ObjectId(id)})
	pattern['_id'] = str(pattern['_id'])
	return pattern

@app.route('/schema', methods=['GET'])
def get_filters():
	# get column names
	with open('schema.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)


@app.route('/pattern/<string:_id>', methods=['GET'])
def get_pattern(_id):
	pattern_data = get_pattern_by_id(_id)

	if not pattern_data:
		return jsonify({'error': 'Pattern not found'}), 404
	return jsonify(pattern_data)

if __name__ == "__main__":
    app.run(debug=False)
