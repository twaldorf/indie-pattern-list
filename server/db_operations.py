from bson import ObjectId

def get_patterns_from_db(collection):
	patterns = list(collection.find({}))
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