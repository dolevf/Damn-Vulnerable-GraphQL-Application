import config
import random
import time
import jwt
from datetime import datetime
from datetime import timedelta
from flask import request
from flask import jsonify
from flask import session
from app import app
from .models import User
from .helpers import *
    


def make_easy_token(request):
    try:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username,password=password).first()
        if not user:
            return None
    except:
        return None

    return  jwt.encode(
                {
                    # Deliberately reflecting unchecked request input
                    # JSON injection is possible (combined with no signature checking)
                    'sub': request.form['username'],
                    'exp': datetime.utcnow() + timedelta(seconds=120000), # Deliberately long
                    'prv': user.roles # Deliberately added to the token
                },
                app.secret_key
            )



def make_hard_token(user):
    # TODO implement CVE-2017-11424 https://snyk.io/vuln/SNYK-PYTHON-PYJWT-40693
    return  jwt.encode(
                {
                    'sub': user.username, # No reflection in hard mode
                    'exp': datetime.utcnow() + timedelta(seconds=3600), # Shorter lifespan
                    'prv': user.roles # In hard mode token signature is verified (see decorators)
                },
                app.secret_key,
            )


def simulate_load():
    loads = [200, 300, 400, 500]
    count = 0
    limit = random.choice(loads)
    while True:
        time.sleep(0.1)
        count += 1
        if count > limit:
            return

def is_port(port):
    if isinstance(port, int):
        if port >= 0 and port <= 65535:
            return True
    return False

def allowed_cmd(cmd):
    if level_is_easy():
        return True
    elif level_is_hard():
        if cmd.startswith(('echo', 'ps' 'whoami', 'tail')):
            return True
    return False

def strip_dangerous_characters(cmd):
    if level_is_easy():
        return cmd
    elif level_is_hard():
        return cmd.replace(';','').replace('&', '')
    return cmd

def on_denylist(query):
    normalized_query = ''.join(query.split())
    queries = [
        'query{systemHealth}',
        '{systemHealth}'
    ]

    if normalized_query in queries:
        return True
    return False

def operation_name_allowed(operation_name):
    opnames_allowed = ['CreatePaste', 'getPastesByUsername', 'getPublicPastes', 'UploadPaste', 'ImportPaste']
    if operation_name in opnames_allowed:
        return True
    return False

def depth_exceeded(depth):
    depth_allowed = config.MAX_DEPTH
    if depth > depth_allowed:
        return True
    return False

def cost_exceeded(qry_fields):
    total_cost_allowed = config.MAX_COST
    total_query_cost = 0

    field_cost = {
        'systemUpdate':10,
    }

    for field in qry_fields:
        if field in field_cost:
            total_query_cost += field_cost[field]

    if total_query_cost > total_cost_allowed:
        return True

    return False