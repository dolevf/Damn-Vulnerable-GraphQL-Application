import requests

from common import GRAPHQL_URL

def test_check_batch_enabled():
    query = """
        query {
            __typename
        }
    """
    r = requests.post(GRAPHQL_URL, verify=False, allow_redirects=True, timeout=4, json=[{"query":query}])
    assert isinstance(r.json(), list)
