from collections import defaultdict
from bson import ObjectId
from flask import Blueprint, request, jsonify, current_app

from server.db_operations import db_get_user_by_id, db_get_user_by_username, get_count_from_db, get_pattern_by_id, get_patterns_from_db, search_collection_for_query
patterns_routes = Blueprint('/patterns', __name__)

# Server all patterns of a specific category, sorted, by the page
@patterns_routes.route('/patterns', methods=['GET'])
def index():
	# Get all patterns from collection
	patterns = get_patterns_from_db(current_app.collection)

	# Filter: Category
	category = request.args.get('category', None)
	if (category):
		cat_patterns = [ pattern for pattern in patterns if pattern['category'] == category ]
		patterns = cat_patterns

	# Sort: Price
	sortBy = request.args.get('SortBy')
	if sortBy == 'price':
		sort_by_price(page_of_patterns, sortBy)

	# Pages: Set up pagination parameters
	page_index = int(request.args.get('page', 1))
	page_size = int(request.args.get('page_length', 54))
	front = (page_index - 1) * page_size
	back = front + page_size

	# Pages: Select only the requested page
	page_of_patterns = patterns[front : back]

	# No patterns: debug
	if not page_of_patterns:
		print("no patterns retrieved from db")

	print(len(page_of_patterns))
	# Count all patterns in db
	count_all = get_count_from_db(current_app.collection)

	response = {
		'metadata': {
			'patterns_returned': len(page_of_patterns),
			'total_patterns': count_all,
			'matching_patterns_count': len(patterns),
			'page': page_index
		},
		'data': page_of_patterns
	}

	return jsonify(response)

# Utility, sort a list of patterns by their price field
# TODO: Deprecate this in favor of MongoDB sorting
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

@patterns_routes.route('/patterns/search', methods=['GET'])
def search_patterns():
	query = request.args.get('query')
	if not query:
		return jsonify([])
	
	patterns = search_collection_for_query(query, current_app.collection)
	if not patterns:
		return jsonify([])
	
	response = {
		"data": patterns,
		"metadata": {
			"patterns_returned": len(patterns)
		}
	}

	return jsonify(response)

@patterns_routes.route('/user/likes', methods=['GET'])
def get_patterns_by_user_likes():
	username = request.args.get('username')
	if not username:
		return jsonify({"error": "Missing user_id field"}), 404
	user = db_get_user_by_username(username, current_app.user_collection)
	patterns = []
	for pattern_id in user.get('lists').get('My List'):
		patterns.append(get_pattern_by_id(pattern_id, collection=current_app.collection))
	
	# TODO: abstract this into a bundle builder function
	bundle = {
		"data": patterns,
		"metadata": {
			"patterns_returned": len(patterns)
		}
	}
	return jsonify(bundle)
	

# Delete a pattern by its database ID
# This is crazy, don't put this in prod
# @patterns_routes.route('/patterns/delete/<string:_id>', methods=['DELETE'])
# def delete_pattern_from_main(_id):
# 	pattern = current_app.collection.delete_one({'_id': ObjectId(_id)})

# 	if not pattern:
# 		return jsonify({'error': 'Pattern not found'}), 404
	
# 	return '', 204

# Return a limit view of patterns, by category, with extra metadata
@patterns_routes.route('/patterns/summary', methods=['GET'])
def get_summary():
	# Limited View: get param
	limit = request.args.get('limit')

	# Get all patterns from db
	patterns = get_patterns_from_db(current_app.collection)

	# Metadata: Count the number of patterns for each category
	# Initialize a dict of counters at 0
	categories = defaultdict(int)
	patterns_by_category = {}

	# Count every pattern, adding categories as they are discovered
	for pattern in patterns:
		cat = pattern.get('category')

		# Increment the count
		categories[cat] = categories.setdefault(cat, 0) + 1

		# Add the category to the dict if it does not yet exist
		if cat not in patterns_by_category:
			patterns_by_category[cat] = []

		if limit and categories[cat] < limit:
			patterns_by_category[cat].append(pattern)
		elif not limit:
			patterns_by_category[cat].append(pattern)

	# Limited View: Serve only a limited number of patterns
	if limit:
		patterns = patterns[0 : limit]

	# Metadata: Count all patterns in db
	count_all = get_count_from_db(current_app.collection)

	response = {
			'metadata': {
				'patterns_returned': len(patterns),
				'total_patterns': count_all,
				'matching_patterns_count': len(patterns),
				'page': 0,
				'pattern_count_by_category': categories
			},
			'data': patterns_by_category
		}

	return jsonify(response)	