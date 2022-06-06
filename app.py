import config
import sys
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sockets import Sockets

app = Flask(__name__, static_folder="static/")
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["UPLOAD_FOLDER"] = config.WEB_UPLOADDIR

sockets = Sockets(app)

app.app_protocol = lambda environ_path_info: 'graphql-ws'

db = SQLAlchemy(app)

if __name__ == '__main__':
  sys.setrecursionlimit(100000)

  os.popen("python3 setup.py").read()

  from core.views import *
  from gevent import pywsgi
  from geventwebsocket.handler import WebSocketHandler
  from version import VERSION

  server = pywsgi.WSGIServer((config.WEB_HOST, int(config.WEB_PORT)), app, handler_class=WebSocketHandler)
  print("DVGA Server Version: {version} Running...".format(version=VERSION))
  server.serve_forever()
