from flask import Flask, jsonify, request
from flask_cors import CORS
import json, csv, os
from pymongo import MongoClient
from bson import ObjectId
from db_operations import get_pattern_by_id, get_patterns_from_db, upsert_pattern

csv_path = 'db.csv'

app = Flask(__name__)

origins = [
	"https://ips-client.vercel.app",
	"https://www.superpatternlist.com",
	"http://localhost:5173"
]

CORS(app, resources={r"/*": {"origins": origins}})

# connect to db
mongo_uri = os.environ.get('MONGODB_URI')
db_name = os.environ.get('DB_NAME')

if not mongo_uri:
	mongo_uri = 'mongodb://127.0.0.1:27017'
	db_name = 'patternlistdev'

client = MongoClient(mongo_uri)

print(mongo_uri, db_name)

db = client[db_name]
# the main production collection, which guarantees schema compliance and high detail and accuracy
collection = db['patterns']
# the collection where new user-uploaded patterns and updates are stored, the "pen"
pen_collection = db['pen']
# the garbage collection 
garbage_collection = db['garbage']

@app.route('/patterns', methods=['GET'])
def index():
		# paginate
		page_index = int(request.args.get('page', 1))
		page_size = int(request.args.get('page_length', 50))
		front = (page_index - 1) * page_size
		back = front + page_size

		patterns = get_patterns_from_db(collection)[front : back]

		if not patterns:
			print("no patterns retrieved from db")

		#sort 
		sortBy = request.args.get('SortBy')
		
		if sortBy == 'price':
			sort_by_price(patterns, sortBy)

		return jsonify(patterns)

def sort_by_price(patterns, sortBy):
	for row in patterns:
		if row['price'][0] != '':
			row['price'] = float( row['price'].replace("$", "") )
		else:
			row['price'] = 0.0
	if sortBy:
		patterns.sort( key=lambda x: x.get( sortBy, '') )
	for row in patterns:
		row['price'] = "${:.2f}".format( row['price'] )

@app.route('/pen', methods=['GET'])
def pen_index():
		# paginate
		page_index = int(request.args.get('page', 1))
		page_size = int(request.args.get('page_length', 50))
		front = (page_index - 1) * page_size
		back = front + page_size

		patterns = get_patterns_from_db(pen_collection)[front : back]

		if not patterns:
			print("no patterns retrieved from db")

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


@app.route('/schema', methods=['GET'])
def get_filters():
	# get column names
	with open('schema.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)

@app.route('/pattern/<string:_id>', methods=['GET'])
def get_pattern(_id):
	pattern_data = get_pattern_by_id(_id, collection)

	if not pattern_data:
		return jsonify({'error': 'Pattern not found'}), 404
	return jsonify(pattern_data)

@app.route('/pen/pattern/<string:_id>', methods=['GET'])
def get_pen_pattern(_id):
	pattern_data = get_pattern_by_id(_id, pen_collection)

	if not pattern_data:
		return jsonify({'error': 'Pattern not found'}), 404
	return jsonify(pattern_data)


@app.route('/pattern/new', methods=['POST'])
def set_pattern():
	pattern = request.json
	
	print(pattern)

	if not pattern:
		return jsonify({'error': 'Empty pattern'}), 403

	if pattern:
		pattern_status = pen_collection.insert_one(pattern)
		print(pattern_status)
	
	return "", 201

@app.route('/pattern/update', methods=['POST'])
def update_pattern():
	old_id = request.args.get('_id')
	pattern = request.json
	pattern['id_to_replace'] = ObjectId(old_id)
	new_pattern = dict((key, value) for key, value in pattern.items() if key != '_id')
	print(new_pattern)

	if not pattern:
		return jsonify({'error': 'Empty pattern'}), 403

	if pattern:
		existing = pen_collection.find_one({'id_to_replace': ObjectId(old_id)})
		if existing:
			pattern_status = pen_collection.update_one({'id_to_replace': ObjectId(old_id)}, {'$set': new_pattern})
		elif not existing:
			pattern_status = pen_collection.insert_one(new_pattern)
	
	# POST does not return anything
	return '', 201


@app.route('/pen/<string:_id>', methods=['DELETE'])
def delete_pattern(_id):
	pattern = pen_collection.find_one({'_id': ObjectId(_id)})

	if not pattern:
		return jsonify({'error': 'Pattern not found'}), 404

	pen_collection.delete_one({'_id': ObjectId(_id)})

	return '', 204

@app.route('/approve/<string:_id>', methods=['POST'])
def apply_pattern(_id):
	pattern = pen_collection.find_one({'_id': ObjectId(_id)})

	if not pattern:
		return jsonify({'error': 'Pattern not found'}), 404
	
	# send this to a prep_incoming_pattern function
	pattern['_id'] = ObjectId(pattern['id_to_replace'])

	upsert_pattern(pattern, collection)

	return '', 201
	
if __name__ == "__main__":
    app.run(debug=False)
