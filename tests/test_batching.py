import requests

from common import URL, GRAPHQL_URL, graph_query

def test_batching():
    queries = [
        {"query":"query BATCH_ABC { pastes { title } }"},
        {"query":"query BATCH_DEF { pastes { content } }"}
    ]

    r = requests.post(GRAPHQL_URL, json=queries)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) == 2
    for i in r.json():
        for paste in i['data']['pastes']:
            for field in paste.keys():
                assert field in ('title', 'content')

def test_batched_operation_names():
    r = requests.get(URL + '/audit')
    assert r.status_code == 200
    assert 'BATCH_ABC' in r.text
    assert 'BATCH_DEF' in r.text
