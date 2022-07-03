import requests

from common import URL, GRAPHQL_URL, graph_query

def test_check_introspect_fields():
    fields = ['pastes', 'paste', 'systemUpdate', 'systemDiagnostics', 'systemDebug', 'systemHealth', 'users', 'readAndBurn', 'search', 'audits', 'deleteAllPastes', 'me']
    r = requests.get(URL + '/difficulty/easy')
    assert r.status_code == 200

    query = """
        query {
        __schema {
            queryType {
              fields {
                name
              }
            }
        }
      }
    """
    r = graph_query(GRAPHQL_URL, query)

    for field in r.json()['data']['__schema']['queryType']['fields']:
        field_name = field['name']
        assert field_name in fields
        assert not field_name not in fields
        fields.remove(field_name)

    assert len(fields) == 0

def test_check_introspect_when_expert_mode():
  query = """
    query {
       __schema {
          __typename
       }
    }
  """
  r = graph_query(GRAPHQL_URL, query, headers={"X-DVGA-MODE":'Expert'})
  assert r.status_code == 200
  assert r.json()['errors'][0]['message'] == '400 Bad Request: Introspection is Disabled'


def test_check_introspect_mutations():
    fields = ['createUser', 'createPaste', 'editPaste', 'login', 'uploadPaste', 'importPaste', 'deletePaste']
    r = requests.get(URL + '/difficulty/easy')
    assert r.status_code == 200

    query = """
        query {
        __schema {
            mutationType {
              fields {
                name
              }
            }
        }
      }
    """
    r = graph_query(GRAPHQL_URL, query)

    for field in r.json()['data']['__schema']['mutationType']['fields']:
        field_name = field['name']
        assert field_name in fields
        assert not field_name not in fields
        fields.remove(field_name)

    assert len(fields) == 0