import os
import requests

from common import URL, GRAPHIQL_URL, GRAPHQL_URL

"""
    DVGA Sanity Check
"""
def test_dvga_is_up():
    """Checks DVGA UI HTML returns correct information"""
    r = requests.get(URL)
    assert 'Damn Vulnerable GraphQL Application' in r.text

def test_graphql_endpoint_up():
    """Checks /graphql is up"""
    r = requests.get(GRAPHQL_URL)
    assert "Must provide query string." in r.json()['errors'][0]['message']

def test_graphiql_endpoint_up():
    """Checks /graphiql is up"""
    r = requests.get(GRAPHIQL_URL)
    assert "Must provide query string." in r.json()['errors'][0]['message']
