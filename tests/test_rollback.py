import requests

from common import URL

def test_check_rollback():
    r = requests.get(URL + '/start_over')
    assert r.status_code == 200
    assert 'Restored to default state' in r.text
