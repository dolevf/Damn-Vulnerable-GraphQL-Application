import config
import sys

from os import urandom
from core.helpers import initialize
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sockets import Sockets
from graphql_ws.gevent import  GeventSubscriptionServer
import logging
import logging.handlers as handlers

app = Flask(__name__, static_folder="static/")
app.secret_key = urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["UPLOAD_FOLDER"] = config.WEB_UPLOADDIR

sockets = Sockets(app)


app.app_protocol = lambda environ_path_info: 'graphql-ws'

db = SQLAlchemy(app)

if __name__ == '__main__':
  sys.setrecursionlimit(100000)

  initialize()

  from core.views import *
  from gevent import pywsgi
  from geventwebsocket.handler import WebSocketHandler
  from version import VERSION

  server = pywsgi.WSGIServer((config.WEB_HOST, int(config.WEB_PORT)), app, handler_class=WebSocketHandler)
  print("DVGA Server Version: {version} Running...".format(version=VERSION))
  server.serve_forever()
