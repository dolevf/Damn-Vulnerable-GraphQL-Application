def get_fields_from_query(q):
  fields = [k for k in q.split() if k.isalnum()]
  return fields

def get_depth(q):
  depth = 0
  for i in q.split():
    if i == '{':
      depth += 1
  return depth
