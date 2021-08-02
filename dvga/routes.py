import jwt 
import graphene 

from datetime import datetime
from datetime import timedelta
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import make_response
from flask import session
from flask_graphql import GraphQLView

import config
from app import app
from app import db
from stuffing import solutions as list_of_solutions
from .decorators import token_required
from .decorators import access_controlled_for
from .helpers import *
from .middleware import *
from .models import User
from .models import Audit
from .schema import Mutations
from .schema import Query
from .security import *



@app.context_processor
def get_version():
    return dict(version=config.VERSION)

@app.before_request
def set_difficulty():
    mode_header = request.headers.get('X-DVGA-MODE', None)
    if mode_header:
        if mode_header == 'Expert':
            set_mode('hard')
        else:
            set_mode('easy')
    else:
        if session.get('difficulty') == None:
            set_mode('easy')

@app.route('/')
def index():
    if session.get('authenticated'):
        resp = make_response(render_template('index.html'))
    else:
        resp = make_response(render_template('login.html'))
     
    # TODO remonve temporary comment out 
    #resp.set_cookie("env", "graphiql:disable")
    return resp



@app.route('/login', methods = ['POST'])
def login():
    token = ""
    if request.form['username'] and request.form['password']:
        username = request.form['username']
        password = request.form['password']
    else:
        rsp = make_response(redirect('/'))
        rsp.headers['WWW-Authenticate'] = 'Basic realm: Authentication failure.'
        return rsp

    if level_is_easy:
        token = make_easy_token(request)

    if level_is_hard:
        # Mutation injection ? :)
        query =     "mutation AuthenticateUser {"              
        query +=    "   loginVerify("
        query +=    "       username: \"" + username + "\","     
        query +=    "       password: \"" + password + "\") {"
        query +=    "           accessToken"
        query +=    "       }"
        query +=    "}"
            
    rsp = make_response(redirect('/'))

    # Deliberately use cookies instead of token submission
    # Deliberately set cookie without "HttpOnly" and obviously without "Secure"
    if token:
        session['authenticated'] = True
        token = app.schema.execute(query).data['loginVerify']['accessToken']
        rsp.set_cookie('dvga_jwt', token)
    else:
        rsp.headers['WWW-Authenticate'] = 'Basic realm: Authentication failure.'
    return rsp


@app.route('/logout')
@token_required
def logout():
    session['authenticated'] = False
    rsp = make_response(redirect('/'))
    rsp.set_cookie('dvga_jwt', "")  
    return rsp

@app.route('/about')
@token_required
@access_controlled_for(allowed_roles='user')
def about():
    return render_template("about.html")

@app.route('/solutions')
@token_required
@access_controlled_for(allowed_roles='user')
def solutions():
    return render_template("solutions.html", solutions=list_of_solutions)

@app.route('/forbidden')
def forbidden():
    return render_template("forbidden.html")

@app.route('/create_paste')
@token_required
@access_controlled_for(allowed_roles='user')
# Left deliberately unauthenticated
def create_paste():
    return render_template("paste.html", page="create_paste")

@app.route('/import_paste')
@token_required
@access_controlled_for(allowed_roles='admin')
def import_paste():
    return render_template("paste.html", page="import_paste")

@app.route('/upload_paste')
@token_required
@access_controlled_for(allowed_roles='user')
def upload_paste():
    return render_template("paste.html", page="upload_paste")

@app.route('/my_pastes')
@token_required
@access_controlled_for(allowed_roles='user')
def my_paste():
    return render_template("paste.html", page="my_pastes")

@app.route('/public_pastes')
@token_required
@access_controlled_for(allowed_roles='user')
def public_paste():
    return render_template("paste.html", page="public_pastes")

@app.route('/audit')
@access_controlled_for(allowed_roles='user')
@token_required
def audit():
    audit = Audit.query.all()
    return render_template("audit.html", audit=audit)


@app.route('/start_over')
def start_over():
    msg = "Restored to default state."
    res = initialize()

    if 'done' not in res:
        msg="Could not restore to default state."

    return render_template('index.html', msg=msg)

@app.route('/difficulty/<level>')
def difficulty(level):
    if level in ('easy', 'hard'):
        message = f'Changed difficulty level to {level.capitalize()}'
    else:
        message = 'Level must be Beginner or Expert.'
        level = 'easy'

    set_mode(level)
    return render_template('index.html', msg=message)