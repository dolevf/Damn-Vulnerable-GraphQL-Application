import config
import random
import ipaddress
import time

from core import helpers

def simulate_load():
  loads = [200, 300, 400, 500]
  count = 0
  limit = random.choice(loads)
  while True:
    time.sleep(0.1)
    count += 1
    if count > limit:
      return

def get_network(addr, style='cidr'):
  try:
    if style == 'cidr':
      return str(ipaddress.ip_network(addr))
    else:
      return str(ipaddress.ip_network(addr).netmask)
  except:
    return 'Could not identify network'

def is_port(port):
  if isinstance(port, int):
    if port >= 0 and port <= 65535:
      return True
  return False

def allowed_cmds(cmd):
  if helpers.is_level_easy():
    return True
  elif helpers.is_level_hard():
    if cmd.startswith(('echo', 'ps' 'whoami', 'tail')):
      return True
  return False

def strip_dangerous_characters(cmd):
  if helpers.is_level_easy():
    return cmd
  elif helpers.is_level_hard():
    return cmd.replace(';','').replace('&', '')
  return cmd

def check_creds(username, password, real_password):
  if username != 'admin':
    return (False, 'Username is invalid')

  if password == real_password:
    return (True, 'Password Accepted.')

  return (False, 'Password Incorrect')

def on_denylist(query):
  normalized_query = ''.join(query.split())
  queries = [
    'query{systemHealth}',
    '{systemHealth}'
  ]

  if normalized_query in queries:
    return True
  return False

def operation_name_allowed(operation_name):
  opnames_allowed = ['CreatePaste', 'EditPaste', 'getPastes', 'UploadPaste', 'ImportPaste']
  if operation_name in opnames_allowed:
    return True
  return False

def depth_exceeded(depth):
  depth_allowed = config.MAX_DEPTH
  if depth > depth_allowed:
    return True
  return False

def cost_exceeded(qry_fields):
  total_cost_allowed = config.MAX_COST
  total_query_cost   = 0

  field_cost = {
    'systemUpdate':10,
  }

  for field in qry_fields:
    if field in field_cost:
      total_query_cost += field_cost[field]

  if total_query_cost > total_cost_allowed:
    return True

  return False