import requests

import uuid

from os import environ

IP =  environ.get('WEB_HOST', '127.0.0.1')
PORT = environ.get('WEB_PORT', 5013)

URL = 'http://{}:{}'.format(IP, PORT)
GRAPHQL_URL = URL + '/graphql'
GRAPHIQL_URL = URL + '/graphiql'

def generate_id():
    return str(uuid.uuid4())[4]

def graph_query(url, query=None, operation="query", headers={}):
    return requests.post(url,
                            verify=False,
                            allow_redirects=True,
                            timeout=30,
                            headers=headers,
                            json={operation:query})