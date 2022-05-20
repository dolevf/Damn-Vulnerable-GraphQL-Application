import werkzeug

from flask import request
from core.decorators import run_only_once

from core import (
  helpers,
  parser,
  security
)

# Middleware
class DepthProtectionMiddleware(object):
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_easy():
      return next(root, info, **kwargs)

    depth = 0
    array_qry = []

    if isinstance(info.context.json, dict):
      array_qry.append(info.context.json)

    elif isinstance(info.context.json, list):
      array_qry = info.context.json

    for q in array_qry:
      query = q.get('query', None)
      mutation = q.get('mutation', None)

      if query:
        depth = parser.get_depth(query)

      elif mutation:
        depth = parser.get_depth(query)

      if security.depth_exceeded(depth):
        raise werkzeug.exceptions.SecurityError('Query Depth Exceeded! Deep Recursion Attack Detected.')

    return next(root, info, **kwargs)

class CostProtectionMiddleware(object):
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_easy():
      return next(root, info, **kwargs)

    fields_requested = []
    array_qry = []

    if isinstance(info.context.json, dict):
      array_qry.append(info.context.json)

    elif isinstance(info.context.json, list):
      array_qry = info.context.json

    for q in array_qry:
      query = q.get('query', None)
      mutation = q.get('mutation', None)

      if query:
        fields_requested += parser.get_fields_from_query(query)
      elif mutation:
        fields_requested += parser.get_fields_from_query(mutation)

    if security.cost_exceeded(fields_requested):
      raise werkzeug.exceptions.SecurityError('Cost of Query is too high.')

    return next(root, info, **kwargs)

class OpNameProtectionMiddleware(object):
  @run_only_once
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_easy():
      return next(root, info, **kwargs)

    try:
      opname = info.operation.name.value
    except:
      opname = "No Operation"

    if opname != 'No Operation' and not security.operation_name_allowed(opname):
      raise werkzeug.exceptions.SecurityError('Operation Name "{}" is not allowed.'.format(opname))

    return next(root, info, **kwargs)


class processMiddleware(object):
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_easy():
      return next(root, info, **kwargs)

    array_qry = []

    if info.context.json is not None:
      if isinstance(info.context.json, dict):
        array_qry.append(info.context.json)

      for q in array_qry:
        query = q.get('query', None)
        if security.on_denylist(query):
          raise werkzeug.exceptions.SecurityError('Query is on the Deny List.')

    return next(root, info, **kwargs)

class IntrospectionMiddleware(object):
  @run_only_once
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_easy():
      return next(root, info, **kwargs)

    if info.field_name.lower() in ['__schema']:
      raise werkzeug.exceptions.SecurityError('Introspection is Disabled')

    return next(root, info, **kwargs)

class IGQLProtectionMiddleware(object):
  @run_only_once
  def resolve(self, next, root, info, **kwargs):
    if helpers.is_level_hard():
      raise werkzeug.exceptions.SecurityError('GraphiQL is disabled')

    cookie = request.cookies.get('env')
    if cookie and cookie == 'graphiql:enable':
      return next(root, info, **kwargs)

    raise werkzeug.exceptions.SecurityError('GraphiQL Access Rejected')
