from config import WEB_UPLOADDIR
from flask import session
import base64
import uuid
import os

def run_cmd(cmd):
  return os.popen(cmd).read()

def initialize():
  return run_cmd('python3 setup.py')

def generate_uuid():
  return str(uuid.uuid4())[0:6]

def decode_base64(text):
  return base64.b64decode(text).decode('utf-8')

def save_file(filename, text):
  try:
    f = open(WEB_UPLOADDIR + filename, 'w')
    f.write(text)
    f.close()
  except Exception as e:
    text = str(e)
  return text

def is_level_easy():
  return session.get('difficulty') == 'easy'

def is_level_hard():
  return session.get('difficulty') == 'hard'

def set_mode(mode):
  session['difficulty'] = mode

def get_opname(operation):
  try:
    return operation.name.value
  except:
    return "No Operation"
