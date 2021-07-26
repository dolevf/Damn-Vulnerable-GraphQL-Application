import base64
import os
import uuid

from config import WEB_UPLOADDIR
from flask import session



def get_fields_from_query(q):
    fields = [k for k in q.split() if k.isalnum()]
    return fields

def get_depth(q):
    depth = 0
    for i in q.split():
        if i == '{':
            depth += 1
    return depth

def run_cmd(cmd):
    return os.popen(cmd).read()

def initialize():
    try:
        out = run_cmd('python setup.py')
        return out
    except Exception as err:
        print('[-] Error: ', err.message)

def generate_uuid():
    return str(uuid.uuid4())[0:6]

def decode_base64(text):
    return base64.b64decode(text).decode('utf-8')

def save_file(filename, text):
    try:
        with open(WEB_UPLOADDIR + filename, 'w') as f:
            f.write(text)
        
    except Exception as e:
        text = str(e)
        return text

def level_is_easy():
    return session.get('difficulty') == 'easy'

def level_is_hard():
    return session.get('difficulty') == 'hard'

def set_mode(mode):
    session['difficulty'] = mode

def get_opname(operation):
    try:
        return operation.name.value
    except:
        return "No Operation"
