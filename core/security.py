import random
import time

def simulate_load():
  loads = [200, 300, 400, 500]
  count = 0
  limit = random.choice(loads)
  while True:
    time.sleep(0.1)
    count += 1
    if count > limit:
      return


def is_port(port):
  if isinstance(port, int):
    if port >= 0 and port <= 65535:
      return True
  return False

def allowed_cmds(cmd):
  if cmd.startswith(('ls', 'head', 'echo', 'find', 'ps', 'whoami')):
    return True
  return False

def strip_dangerous_characters(cmd):
  return cmd.replace('"', '').replace(';','').replace('|', '')

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
    '{systemHealth}',
    'query{__schema{types{name}}}',
    '{__schema{types{name}}}',
    'query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}}}'
  ]

  if normalized_query in queries:
    return True
  return False