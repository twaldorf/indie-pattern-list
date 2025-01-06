import os
from pymongo import MongoClient

def init_db(test_config=None):
	if test_config is None:
		mongo_uri = 'mongodb://127.0.0.1:27017'
		db_name = 'patternlistdev'
		collection_name = 'patterns'
		pen_name = 'pen'
		garbage_name = 'garbage'
		users_name = 'users'
	elif test_config:
		mongo_uri = test_config['MONGO_URI']
		db_name = test_config['DB_NAME']
		collection_name = test_config['COLLECTION']
		pen_name = test_config['PEN_COLLECTION']
		garbage_name = test_config['GARBAGE_COLLECTION']
		users_name = test_config['USERS']

	# Get database info from environment for Heroku usage
	if (os.environ.get('MONGODB_URI')):
		mongo_uri = os.environ.get('MONGODB_URI')
		db_name = os.environ.get('DB_NAME')

	# initialize client connection and select database
	client = MongoClient(mongo_uri)
	db = client[db_name]
	# the main production collection, which guarantees schema compliance and high detail and accuracy
	collection = db[collection_name]
	# the collection where new user-uploaded patterns and updates are stored, the "pen"
	pen_collection = db[pen_name]
	# the garbage collection 
	garbage_collection = db[garbage_name]
	users_collection = db[users_name]

	db_package = {
		'COLLECTION': collection,
		'PEN': pen_collection,
		'GARBAGE': garbage_collection,
		'USERS': users_collection
	}
	return db_package