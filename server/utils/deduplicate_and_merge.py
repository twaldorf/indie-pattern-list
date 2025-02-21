from setup import setup

collection = setup();

patterns = collection.find({})
for pattern in patterns:
  duplicates = collection.find({'title': pattern['title']})
  if duplicates:
    for dup in duplicates:
      # Case: dup is not the base pattern
      if dup['_id'] != pattern['_id']:
      # If the duplicate has different keys, aggregate them and update the pattern
      # If the duplicate is a true duplicate, delete it
        pattern_less_id = {k:v for k,v in pattern.items() if k != '_id'}
        dup_less_id = {k:v for k,v in dup.items() if k != '_id'}
        
        if pattern_less_id == dup_less_id or set(dup_less_id.keys()).issubset(set(pattern_less_id.keys())):
          # Dup is a true duplicate with no difference in keys, or is a subset, delete it
          res = collection.delete_one({'_id': dup['_id']})
          print(res)
        else:
          dkeys = dict.keys(dup)
          for key in dkeys:
            if ( key != '_id' ) and ( pattern.get(key) == None or len(pattern[key]) < 1):
              pattern[key] = dup[key]
        
          # This is indented incorrectly
          update = { '$set': pattern }
          res = collection.update_one({'_id': pattern['_id']}, update)
          print(res)

