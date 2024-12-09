from flask import Flask, jsonify, request
from flask_cors import CORS
import json, csv, os
from pymongo import MongoClient
from bson import ObjectId
from .db_operations import get_count_from_db, get_pattern_by_id, get_patterns_from_db, search_collection_for_query, upsert_pattern
from collections import defaultdict
from .db_manager import init_db
from .routes.patterns import pattern_routes

# move to config file
# csv_path = 'db.csv'
origins = [
	"https://ips-client.vercel.app",
	"https://www.superpatternlist.com",
	"http://localhost:5173"
]

# App Factory for production, debug, and test
def create_app(test_config=None):
	app = Flask(__name__)
	CORS(app, resources={r"/*": {"origins": origins}})

	# TODO: Rewrite all of this
	# this is bananas noodleman logic
	if test_config is None:
		db_package = init_db()
	else:
		db_package = init_db(test_config)

	# TODO: Condense these, include app. prefix in all functions
	collection = db_package['COLLECTION']
	pen_collection = db_package['PEN']
	garbage_collection = db_package['GARBAGE']

	app.collection = collection
	app.pen_collection = pen_collection
	app.garbage_collection = garbage_collection

	# Register Blueprinted routes
	app.register_blueprint(pattern_routes)

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

		response = {
			"ObjectId": str(pattern_status.inserted_id)
		}
		
		return jsonify(response), 201

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
		if ('id_to_replace' in pattern):
			pattern['_id'] = ObjectId(pattern['id_to_replace'])

		upsert_pattern(pattern, collection)

		return '', 201

	# @app.route('/patterns/search', methods=['GET'])
	# def search_patterns():
	# 	query = request.args.get('query')
	# 	if not query:
	# 		return jsonify([])
		
	# 	patterns = search_collection_for_query(query, collection)
	# 	if not patterns:
	# 		return jsonify([])
		
	# 	response = {
	# 		"data": patterns,
	# 		"metadata": {
	# 			"patterns_returned": len(patterns)
	# 		}
	# 	}

	# 	return jsonify(response)
	
	# factory makes an app
	return app
	

if __name__ == "__main__":
	app = create_app()
	app.run(debug=False)
else:
	app = create_app()