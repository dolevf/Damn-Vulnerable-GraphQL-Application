import datetime

from app import db
import re
from graphql import parse
from graphql.execution.base import ResolveInfo

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)

    @classmethod
    def create_user(cls, **kw):
      obj = cls(**kw)
      db.session.add(obj)
      db.session.commit()

      return obj


def clean_query(gql_query):
  clean = re.sub(r'(?<=token:")(.*)(?=")', "*****", gql_query)
  clean = re.sub(r'(?<=password:")(.*)(?=")', "*****", clean)
  return clean


class Audit(db.Model):
  __tablename__ = 'audits'
  id = db.Column(db.Integer, primary_key=True)
  gqloperation = db.Column(db.String)
  gqlquery = db.Column(db.String)
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  @classmethod
  def create_audit_entry(cls, info, subscription_type=False):
    gql_query = '{}'
    gql_operation = None
    obj = False

    """
      GraphQL subscriptions pass a String, conversion to AST is required.
    """
    if subscription_type and isinstance(info, str):
      """Subscriptions"""
      gql_query = info
      ast = parse(gql_query)

      try:
        gql_operation = ast.definitions[0].name.value
      except:
        gql_operation = 'No Operation'

      obj = cls(**{"gqloperation":gql_operation, "gqlquery":gql_query})
      db.session.add(obj)
    else:
      """Queries and Mutations"""
      try:
        gql_operation = info.operation.name.value
      except:
        gql_operation = "No Operation"

      if isinstance(info, ResolveInfo):
        if isinstance(info.context.json, list):
          """Array-based Batch"""
          for i in info.context.json:
            gql_query = i.get("query")
            gql_query = clean_query(gql_query)
            obj = cls(**{"gqloperation":gql_operation, "gqlquery":gql_query})
            db.session.add(obj)
        else:
          if info.context.json:
            gql_query = info.context.json.get("query")
            gql_query = clean_query(gql_query)
            obj = cls(**{"gqloperation":gql_operation, "gqlquery":gql_query})
            db.session.add(obj)

    db.session.commit()
    return obj

class Owner(db.Model):
  __tablename__ = 'owners'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  paste = db.relationship('Paste', lazy='dynamic', overlaps="pastes")


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
    backref='pastes',
    overlaps="paste"
  )
  burn = db.Column(db.Boolean, default=False)

  @classmethod
  def create_paste(cls, **kw):
    obj = cls(**kw)
    db.session.add(obj)
    db.session.commit()

    return obj

class ServerMode(db.Model):
  __tablename__ = 'servermode'
  id = db.Column(db.Integer, primary_key=True)
  hardened = db.Column(db.Boolean, default=False)

  @classmethod
  def set_mode(cls, mode):
    obj = ServerMode.query.one()
    if mode == 'easy':
      obj.hardened = False
    else:
      obj.hardened = True

    db.session.add(obj)
    db.session.commit()

    return obj