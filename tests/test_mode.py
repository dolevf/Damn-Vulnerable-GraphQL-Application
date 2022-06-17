import requests

from common import URL, GRAPHQL_URL, graph_query

def test_check_hardened_mode():
    r = requests.get(URL + '/difficulty/hard')
    assert r.status_code == 200

    query = """
        query {
            __schema {
                __typename
            }
        }
    """
    r = graph_query(GRAPHQL_URL, query)
    assert r.json()['errors'][0]['message'] == '400 Bad Request: Introspection is Disabled'

def test_check_easy_mode():
    r = requests.get(URL + '/difficulty/easy')
    assert r.status_code == 200

    query = """
        query {
            __schema {
                __typename
            }
        }
    """
    r = graph_query(GRAPHQL_URL, query)
    assert r.json()['data']['__schema']['__typename'] == '__Schema'
