import requests

from common import URL, GRAPHQL_URL, graph_query

def test_mutation_createPaste():
    query = '''
    mutation {
      createPaste(burn: false, title:"Integration Test", content:"Test", public: false) {
        paste {
        burn
        title
        content
        public
        owner {
            id
            name
          }
        }
      }
    }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['createPaste']['paste']['burn'] == False
    assert r.json()['data']['createPaste']['paste']['title'] == 'Integration Test'
    assert r.json()['data']['createPaste']['paste']['content'] == 'Test'
    assert r.json()['data']['createPaste']['paste']['public'] == False
    assert r.json()['data']['createPaste']['paste']['owner']['id']
    assert r.json()['data']['createPaste']['paste']['owner']['name']

def test_mutation_editPaste():
    query = '''
    mutation {
        editPaste(id: 1, title:"Integration Test123", content:"Integration Test456") {
            paste {
                id
                title
                content
                userAgent
                burn
                ownerId
                owner {
                    id
                    name
                }
            }
        }
    }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['editPaste']['paste']['id'] == '1'
    assert r.json()['data']['editPaste']['paste']['title'] == 'Integration Test123'
    assert r.json()['data']['editPaste']['paste']['content'] == 'Integration Test456'
    assert r.json()['data']['editPaste']['paste']['userAgent']
    assert r.json()['data']['editPaste']['paste']['burn'] == False
    assert r.json()['data']['editPaste']['paste']['ownerId']
    assert r.json()['data']['editPaste']['paste']['owner']['id'] == '1'
    assert r.json()['data']['editPaste']['paste']['owner']['name']

def test_mutation_deletePaste():
    query = '''
        mutation {
            deletePaste(id: 91000) {
                result
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['deletePaste']['result'] == False

    query = '''
        mutation {
            deletePaste(id: 5) {
                result
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['deletePaste']['result'] == True

def test_mutation_uploadPaste():
    query = '''
        mutation {
            uploadPaste(content:"Uploaded Content", filename:"test.txt") {
                result
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['uploadPaste']['result'] == "Uploaded Content"

    query = '''
        query {
            pastes {
                content
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    found = False
    for i in r.json()['data']['pastes']:
        if i['content'] == 'Uploaded Content':
            found = True

    assert found == True


def test_mutation_importPaste():
    query = '''
        mutation {
            importPaste(scheme: "https", host:"icanhazip.com", path:"/", port:443) {
                 result
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['importPaste']['result']
    assert '.' in r.json()['data']['importPaste']['result']


def test_mutation_createUser():
    query = '''
    mutation {
        createUser(userData:{username:"integrationuser", password:"strongpass"}) {
            user {
             username
            }
        }
    }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.json()['data']['createUser']['user']['username'] == 'integrationuser'

def test_mutation_createBurnPaste():
    query = '''
        mutation {
            createPaste(burn: true, content: "Burn Me", title: "Burn Me", public: true) {
                paste {
                  content
                  burn
                  title
                  id
                }
            }
        }
    '''
    r = graph_query(GRAPHQL_URL, query)

    assert r.status_code == 200
    assert r.json()['data']['createPaste']['paste']['content'] == 'Burn Me'
    assert r.json()['data']['createPaste']['paste']['title'] == 'Burn Me'
    assert r.json()['data']['createPaste']['paste']['id']

    paste_id = r.json()['data']['createPaste']['paste']['id']

    query = '''
        query {
            readAndBurn(id: %s) {
                content
                burn
                title
                id
            }
        }
    ''' % paste_id

    r = graph_query(GRAPHQL_URL, query)

    assert r.status_code == 200
    assert r.json()['data']['readAndBurn']['content'] == 'Burn Me'
    assert r.json()['data']['readAndBurn']['title'] == 'Burn Me'
    assert r.json()['data']['readAndBurn']['id']


    query = '''
        query {
            readAndBurn(id: %s) {
                content
                burn
                title
                id
            }
        }
    ''' % paste_id
    r = graph_query(GRAPHQL_URL, query)

    assert r.status_code == 200
    assert r.json()['data']['readAndBurn'] == None

