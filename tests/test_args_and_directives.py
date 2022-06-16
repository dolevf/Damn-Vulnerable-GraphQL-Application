from common import GRAPHQL_URL, graph_query

def test_capitalize_field_argument():
  query = '''
    query {
      users {
        username(capitalize: true)
      }
    }
    '''
  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['users'][0]['username'] in ('Admin', 'Operator')

def test_show_network_directive():
  query = '''
    query {
      pastes {
          ipAddr @show_network(style:"cidr")
      }
    }
  '''
  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['pastes'][0]['ipAddr'].endswith('/32')

  query = '''
    query {
      pastes {
        ipAddr @show_network(style:"netmask")
      }
    }
  '''
  r = graph_query(GRAPHQL_URL, query)

  assert r.json()['data']['pastes'][0]['ipAddr'].startswith('255.255.')