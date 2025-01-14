from bson import ObjectId

# Pattern operations
def get_patterns_from_db(collection):
	patterns = list(collection.find({}).sort('_id', -1))
	for pattern in patterns:
		prepare_outgoing_pattern(pattern)
	
	return patterns

def get_count_from_db(collection):
	count = collection.count_documents({})
	return count


def get_pattern_by_id(id, collection):
	pattern = collection.find_one({'_id': ObjectId(id)})
	if pattern:
		prepare_outgoing_pattern(pattern)

	return pattern

# Utility to handle BSON IDs on outgoing patterns
def prepare_outgoing_pattern(pattern):
  pattern['_id'] = str(pattern['_id'])
  if 'id_to_replace' in pattern:
    pattern['id_to_replace'] = str(pattern['id_to_replace'])

def upsert_pattern(pattern, collection):
	collection.update_one({'_id': pattern['_id']}, {'$set': pattern}, upsert=True)
	
def search_collection_for_query(query, collection):
  patterns = list(collection.find({'$text': {'$search': query}}))
  for pattern in patterns:
    prepare_outgoing_pattern(pattern)
  
  return patterns

# User operations
def db_get_user_by_id(_id, collection):
	user = collection.find_one({'_id': ObjectId(_id)})
	return user

def db_get_user_by_username(username, collection):
	return collection.find_one({'username': username})

def db_create_user(user, collection):
	return collection.insert_one({'username': user['username'], 'password_hash': user['password_hash']})

def db_update_user(user, collection):
	print(user)
	return collection.update_one({'_id': user['_id']}, {'$set': {'lists': user['lists']}})

def db_collect_pattern(userId, collection, pid, listName):
	user = db_get_user_by_id(userId, collection)
	if user:
		if not user.get('lists'):
			user['lists'] = {}

		user['lists'].setdefault(listName, [])
		user['lists'][listName].append(pid)
		result = db_update_user(user, collection)
		return result
	return False

# def db_get_lists(userId, collection):
# 	user = db_get_user_by_id(userId, collection)
# 	if user['lists']:

