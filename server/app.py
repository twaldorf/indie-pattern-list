from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json, csv, os
from flask_login import LoginManager, current_user, login_required
from pymongo import MongoClient
from bson import ObjectId

from .auth.user import User
from .db_operations import get_pattern_by_id, get_patterns_from_db, upsert_pattern
from collections import defaultdict
from .db_manager import init_db
from .routes.patterns import patterns_routes
from .routes.pattern import pattern_routes
from .auth.auth import login_routes

# move to config file
# csv_path = 'db.csv'
origins = [
	"https://ips-client.vercel.app",
	"https://www.superpatternlist.com",
	"http://localhost:5173",
	"http://10.0.0.73:5173"
]

# App Factory for production, debug, and test
def create_app(test_config=None):
	app = Flask(__name__)

	app.secret_key = os.environ.get('FLASK_SECRET_KEY')
	app.config.update(
		SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict'
	)

	CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)

	limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
	)

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

	# Old style
	app.collection = collection
	app.pen_collection = pen_collection
	app.garbage_collection = garbage_collection

	# New style
	app.user_collection = db_package['USERS']
	
	# Initialize login manager
	login_manager = LoginManager()
	login_manager.init_app(app)
	# Attach login manager as an attribute of the app
	app.login_manager = login_manager

	# Register Blueprinted routes
	app.register_blueprint(pattern_routes)
	app.register_blueprint(patterns_routes)
	app.register_blueprint(login_routes)


	# Holding zone for user management logic
	# Define user loader callback
	@login_manager.user_loader
	def load_user(user_id):
		return User.get_by_id(user_id, app.user_collection)

	# Untested, unused
	@app.route('/current_user/', methods=['GET'])
	@login_required
	def get_current_user():
		user = current_user
		return jsonify(user), 201
	
	@app.route('/user/likes/', methods=['POST'])
	@login_required
	def add_like():
		pattern_id = request.args.id
		current_user.addLike(pattern_id)
		return jsonify("Success, user added")

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

	@app.route('/schema', methods=['GET'])
	def get_filters():
		# get column names
		with open('schema.json', 'r') as file:
			data = json.load(file)

		return jsonify(data)

	@app.route('/pen/pattern/<string:_id>', methods=['GET'])
	def get_pen_pattern(_id):
		pattern_data = get_pattern_by_id(_id, pen_collection)

		if not pattern_data:
			return jsonify({'error': 'Pattern not found'}), 404
		return jsonify(pattern_data)


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