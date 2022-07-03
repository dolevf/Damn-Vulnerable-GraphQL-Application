import requests

from common import GRAPHQL_URL, graph_query

def test_mutation_login_success():
  query = '''
  mutation {
    login(username: "operator", password:"password123") {
      accessToken
    }
  }
  '''
  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['login']['accessToken']


def test_mutation_login_error():
  query = '''
  mutation {
    login(username: "operator", password:"dolevwashere") {
      accessToken
    }
  }
  '''
  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['errors'][0]['message'] == 'Authentication Failure'


def test_query_me():
  query = '''
  query {
    me(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNjU2ODE0OTQ4LCJuYmYiOjE2NTY4MTQ5NDgsImp0aSI6ImI5N2FmY2QwLTUzMjctNGFmNi04YTM3LTRlMjdjODY5MGE2YyIsImlkZW50aXR5IjoiYWRtaW4iLCJleHAiOjE2NTY4MjIxNDh9.-56ZQN9jikpuuhpjHjy3vLvdwbtySs0mbdaSq-9RVGg") {
      id
      username
      password
    }
  }
  '''

  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['me']['id'] == '1'
  assert r.json()['data']['me']['username'] == 'admin'
  assert r.json()['data']['me']['password'] == 'changeme'


def test_query_me_operator():
  query = '''
  query {
    me(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNjU2ODE0OTQ4LCJuYmYiOjE2NTY4MTQ5NDgsImp0aSI6ImI5N2FmY2QwLTUzMjctNGFmNi04YTM3LTRlMjdjODY5MGE2YyIsImlkZW50aXR5Ijoib3BlcmF0b3IiLCJleHAiOjE2NTY4MjIxNDh9.iZ-Sifz1WEkcy1CwX4c-rzI-QgfzUMqpWr2oYr8vZ1o") {
      id
      username
      password
    }
  }
  '''

  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['me']['id'] == '2'
  assert r.json()['data']['me']['username'] == 'operator'
  assert r.json()['data']['me']['password'] == '******'