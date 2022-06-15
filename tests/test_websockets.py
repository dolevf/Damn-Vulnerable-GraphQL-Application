import requests

from common import URL

def test_check_websocket():
    headers = {
        "Connection":"Upgrade",
        "Upgrade":"websocket",
        "Host":"localhost",
        "Origin":"localhost",
        "Sec-WebSocket-Version":"13",
        "Sec-WebSocket-Key":"+onQ3ZxjWlkNa0na6ydhNg=="
    }

    r = requests.get(URL, headers=headers)
    assert r.status_code == 101
    assert r.headers['Upgrade'] == 'websocket'
    assert r.headers['Connection'] == 'Upgrade'
    assert r.headers['Sec-WebSocket-Accept']

