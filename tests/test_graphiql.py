import requests

from common import GRAPHIQL_URL

def test_check_batch_disabled():
    query = """
        query {
            __typename
        }
    """
    r = requests.post(GRAPHIQL_URL, verify=False, allow_redirects=True, timeout=4, json=[{"query":query}])
    assert not isinstance(r.json(), list)
    assert r.json()['errors'][0]['message'] == 'Batch GraphQL requests are not enabled.'
