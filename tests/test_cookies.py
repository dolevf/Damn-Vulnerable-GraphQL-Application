import requests

from common import URL

def test_check_graphiql_cookie():
    r = requests.get(URL + '/')
    assert r.status_code == 200
    assert 'env=graphiql:disable' in r.headers.get('Set-Cookie')

