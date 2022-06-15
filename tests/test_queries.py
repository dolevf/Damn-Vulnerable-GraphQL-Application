import requests

from common import URL, GRAPHQL_URL, graph_query

def test_query_pastes():
    query = '''
    query {
      pastes {
        id
        ipAddr
        ownerId
        burn
        owner {
            id
            name
        }
        title
        content
        userAgent
      }
    }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['pastes'][0]['id']
    assert r.json()['data']['pastes'][0]['ipAddr'] == '127.0.0.1'
    assert r.json()['data']['pastes'][0]['ownerId'] == 1
    assert r.json()['data']['pastes'][0]['burn'] == False
    assert r.json()['data']['pastes'][0]['owner']['id'] == '1'
    assert r.json()['data']['pastes'][0]['owner']['name'] == 'DVGAUser'
    assert r.json()['data']['pastes'][0]['title']
    assert r.json()['data']['pastes'][0]['userAgent']
    assert r.json()['data']['pastes'][0]['content']

def test_query_paste_by_id():
    query = '''
    query {
      paste (id: 1) {
        id
        ipAddr
        ownerId
        burn
        owner {
            id
            name
        }
        title
        content
        userAgent
      }
    }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['paste']['id'] == '1'
    assert r.json()['data']['paste']['ipAddr'] == '127.0.0.1'
    assert r.json()['data']['paste']['ownerId'] == 1
    assert r.json()['data']['paste']['burn'] == False
    assert r.json()['data']['paste']['owner']['id'] == '1'
    assert r.json()['data']['paste']['owner']['name'] == 'DVGAUser'
    assert r.json()['data']['paste']['title'] == 'Testing Testing'
    assert r.json()['data']['paste']['userAgent'] == 'User-Agent not set'
    assert r.json()['data']['paste']['content'] == 'My First Paste'

def test_query_paste_by_title():
    query = '''
        query {
        paste (title: "Testing Testing") {
            id
            ipAddr
            ownerId
            burn
            owner {
                id
                name
            }
            title
            content
            userAgent
        }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['paste']['id'] == '1'
    assert r.json()['data']['paste']['ipAddr'] == '127.0.0.1'
    assert r.json()['data']['paste']['ownerId'] == 1
    assert r.json()['data']['paste']['burn'] == False
    assert r.json()['data']['paste']['owner']['id'] == '1'
    assert r.json()['data']['paste']['owner']['name'] == 'DVGAUser'
    assert r.json()['data']['paste']['title'] == 'Testing Testing'
    assert r.json()['data']['paste']['userAgent'] == 'User-Agent not set'
    assert r.json()['data']['paste']['content'] == 'My First Paste'

def test_query_systemHealth():
    query = '''
        query {
           systemHealth
        }
    '''
    r = graph_query(GRAPHQL_URL, query)
    assert 'System Load' in r.json()['data']['systemHealth']
    assert '.' in r.json()['data']['systemHealth'].split('System Load: ')[1]
