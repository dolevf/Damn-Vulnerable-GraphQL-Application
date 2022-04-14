import datetime

from app import db
from core import helpers
from sqlalchemy import event
from graphql import parse

from rx import Observable

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)

    @classmethod
    def create_user(cls, **kw):
      obj = cls(**kw)
      db.session.add(obj)
      db.session.commit()

      return obj

class Audit(db.Model):
  __tablename__ = 'audits'
  id = db.Column(db.Integer, primary_key=True)
  gqloperation = db.Column(db.String)
  gqlquery = db.Column(db.String)
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  @classmethod
  def create_audit_entry(cls, info, operation_type=None):
    gql_query = '{}'
    gql_operation = None

    if not operation_type:
      gql_operation = helpers.get_opname(info.operation)
      
      if info.context.json:
        gql_query = info.context.json.get("query")
    
    if operation_type == 'subscription' and info:
      ast = parse(info)
      gql_query = info
      
      try:
        gql_operation = ast.definitions[0].name.value
      except:
        pass
      
    obj = cls(**{"gqloperation":gql_operation, "gqlquery":gql_query})
    db.session.add(obj)
    db.session.commit()
    return obj

class Owner(db.Model):
  __tablename__ = 'owners'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  paste = db.relationship('Paste', lazy='dynamic')


class Paste(db.Model):
  __tablename__ = 'pastes'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String)
  content = db.Column(db.String)
  public = db.Column(db.Boolean, default=False)
  user_agent = db.Column(db.String, default=None)
  ip_addr = db.Column(db.String)
  owner_id = db.Column(db.Integer, db.ForeignKey(Owner.id))
  owner = db.relationship(
    Owner,
    backref='pastes'
  )
  burn = db.Column(db.Boolean, default=False)

  @classmethod
  def create_paste(cls, **kw):
    obj = cls(**kw)
    db.session.add(obj)
    db.session.commit()

    return obj
