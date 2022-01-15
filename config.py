import os

# SQLAlchemy
SQLALCHEMY_FILE = f"{os.getcwd()}/dvga.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLALCHEMY_FILE}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask
WEB_HOST  = os.environ.get('WEB_HOST', '127.0.0.1')
WEB_PORT  = os.environ.get('WEB_PORT', 5013)
WEB_DEBUG = os.environ.get('WEB_DEBUG', True)
WEB_UPLOADDIR = 'pastes/'

# GraphQL Security Protection
MAX_DEPTH = 8
MAX_COST = 10