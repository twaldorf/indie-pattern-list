from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from ..db_operations import get_pattern_by_id

pattern_routes = Blueprint('/pattern', __name__)

@pattern_routes.route('/pattern/<string:_id>', methods=['GET'])
def get_pattern(_id):
	pattern_data = get_pattern_by_id(_id, current_app.collection)

	if not pattern_data:
		return jsonify({'error': 'Pattern not found'}), 404
	return jsonify(pattern_data)

@pattern_routes.route('/pattern/new', methods=['POST'])
def set_pattern():
	pattern = request.json
	
	print(pattern)

	if not pattern:
		return jsonify({'error': 'Empty pattern'}), 403

	if pattern:
		pattern_status = current_app.pen_collection.insert_one(pattern)
		print(pattern_status)

	response = {
		"ObjectId": str(pattern_status.inserted_id)
	}
	
	return jsonify(response), 201

@pattern_routes.route('/pattern/update', methods=['POST'])
def update_pattern():
	old_id = request.args.get('_id')
	pattern = request.json
	pattern['id_to_replace'] = ObjectId(old_id)
	new_pattern = dict((key, value) for key, value in pattern.items() if key != '_id')
	print(new_pattern)

	if not pattern:
		return jsonify({'error': 'Empty pattern'}), 403

	if pattern:
		existing = current_app.pen_collection.find_one({'id_to_replace': ObjectId(old_id)})
		if existing:
			pattern_status = current_app.pen_collection.update_one({'id_to_replace': ObjectId(old_id)}, {'$set': new_pattern})
		elif not existing:
			pattern_status = current_app.pen_collection.insert_one(new_pattern)
	
	# POST does not return anything
	return '', 201