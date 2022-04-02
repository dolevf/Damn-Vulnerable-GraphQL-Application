import graphene

from core.directives import *
from db.solutions import solutions as list_of_solutions

from flask import (
  request,
  render_template,
  make_response,
  session
)

from flask_graphql import GraphQLView
from sqlalchemy.sql import text
from graphene_sqlalchemy import (
  SQLAlchemyObjectType
)

from app import app, db

from core import (
  security,
  helpers,
  middleware
)

from core.models import (
  Owner,
  Paste,
  User,
  Audit
)

from version import VERSION

# SQLAlchemy Types
class UserObject(SQLAlchemyObjectType):
  class Meta:
    model = User
    exclude_fields = ('password',)

class PasteObject(SQLAlchemyObjectType):
  class Meta:
    model = Paste
  
  def resolve_ip_addr(self, info):
    for field_ast in info.field_asts:
      for i in field_ast.directives:
        if i.name.value == 'show_network':
          if i.arguments[0].name.value == 'style':
            return security.get_network(self.ip_addr, style=i.arguments[0].value.value)
    return self.ip_addr

class OwnerObject(SQLAlchemyObjectType):
  class Meta:
    model = Owner
    
class CreatePaste(graphene.Mutation):
    paste = graphene.Field(lambda:PasteObject)

    class Arguments:
      title = graphene.String()
      content = graphene.String()
      public = graphene.Boolean(required=False, default_value=True)
      burn = graphene.Boolean(required=False, default_value=False)

    def mutate(self, info, title, content, public, burn):
      owner = Owner.query.filter_by(name='DVGAUser').first()

      paste_obj = Paste.create_paste(
        title=title,
        content=content, public=public, burn=burn,
        owner_id=owner.id, owner=owner, ip_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
      )

      Audit.create_audit_entry(info)

      return CreatePaste(paste=paste_obj)

class DeletePaste(graphene.Mutation):
  result = graphene.Boolean()

  class Arguments:
    id = graphene.Int()


  def mutate(self, info, id):
    result = False
    
    if Paste.query.filter_by(id=id).delete():
      result = True
      db.session.commit() 

    Audit.create_audit_entry(info)

    return DeletePaste(result=result)

class UploadPaste(graphene.Mutation):
  content = graphene.String()
  filename = graphene.String()

  class Arguments:
    content = graphene.String(required=True)
    filename = graphene.String(required=True)

  result = graphene.String()

  def mutate(self, info, filename, content):
    result = helpers.save_file(filename, content)
    owner = Owner.query.filter_by(name='DVGAUser').first()

    Paste.create_paste(
      title='Imported Paste from File - {}'.format(helpers.generate_uuid()),
      content=content, public=False, burn=False,
      owner_id=owner.id, owner=owner, ip_addr=request.remote_addr,
      user_agent=request.headers.get('User-Agent', '')
    )

    Audit.create_audit_entry(info)

    return UploadPaste(result=result)

class ImportPaste(graphene.Mutation):
  result = graphene.String()

  class Arguments:
    host = graphene.String(required=True)
    port = graphene.Int(required=False)
    path = graphene.String(required=True)
    scheme = graphene.String(required=True)

  def mutate(self, info, host='pastebin.com', port=443, path='/', scheme="http"):
    url = security.strip_dangerous_characters(f"{scheme}://{host}:{port}{path}")
    cmd = helpers.run_cmd(f'curl --insecure {url}')

    owner = Owner.query.filter_by(name='DVGAUser').first()
    Paste.create_paste(
        title='Imported Paste from URL - {}'.format(helpers.generate_uuid()),
        content=cmd, public=False, burn=False,
        owner_id=owner.id, owner=owner, ip_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )

    Audit.create_audit_entry(info)

    return ImportPaste(result=cmd)

class Mutations(graphene.ObjectType):
  create_paste = CreatePaste.Field()
  delete_paste = DeletePaste.Field()
  upload_paste = UploadPaste.Field()
  import_paste = ImportPaste.Field()

class Query(graphene.ObjectType):
  pastes = graphene.List(PasteObject, public=graphene.Boolean(), limit=graphene.Int(), filter=graphene.String())
  paste = graphene.Field(PasteObject, id=graphene.Int(), title=graphene.String())
  system_update = graphene.String()
  system_diagnostics = graphene.String(username=graphene.String(), password=graphene.String(), cmd=graphene.String())
  system_debug = graphene.String(arg=graphene.String())
  system_health = graphene.String()
  users = graphene.List(UserObject, id=graphene.Int())
  read_and_burn = graphene.Field(PasteObject, id=graphene.Int())

  def resolve_pastes(self, info, public=False, limit=1000, filter=None):
    query = PasteObject.get_query(info)
    Audit.create_audit_entry(info)
    result = query.filter_by(public=public, burn=False)
    
    if filter:
      result = result.filter(text("title = '%s' or content = '%s'" % (filter, filter)))
    
    return result.order_by(Paste.id.desc())

  def resolve_paste(self, info, id=None, title=None):
    query = PasteObject.get_query(info)
    Audit.create_audit_entry(info)
    if title:
      return query.filter_by(title=title, burn=False).first()
    
    return query.filter_by(id=id, burn=False).first()
      
  def resolve_system_update(self, info):
    security.simulate_load()
    Audit.create_audit_entry(info)
    return 'no updates available'

  def resolve_system_diagnostics(self, info, username, password, cmd='whoami'):
    q = User.query.filter_by(username='admin').first()
    real_passw = q.password
    res, msg = security.check_creds(username, password, real_passw)
    Audit.create_audit_entry(info)
    if res:
      output = f'{cmd}: command not found'
      if security.allowed_cmds(cmd):
        output = helpers.run_cmd(cmd)
      return output
    return msg
  
  def resolve_system_debug(self, info, arg=None):
    Audit.create_audit_entry(info)
    if arg:
      output = helpers.run_cmd('ps {}'.format(arg))
    else:
      output = helpers.run_cmd('ps')
    return output
    
  def resolve_read_and_burn(self, info, id):
    result = Paste.query.filter_by(id=id, burn=True).first()
    Paste.query.filter_by(id=id, burn=True).delete()
    db.session.commit()
    Audit.create_audit_entry(info)
    return result

  def resolve_system_health(self, info):
    Audit.create_audit_entry(info)
    return 'System Load: {}'.format(
      helpers.run_cmd("uptime | awk '{print $10, $11, $12}'")
    )

  def resolve_users(self, info, id=None):
    query = UserObject.get_query(info)
    Audit.create_audit_entry(info)
    if id:
      result = query.filter_by(id=id)
    else:
      result = query
      
    return result



@app.route('/')
def index():
  resp = make_response(render_template('index.html'))
  resp.set_cookie("env", "graphiql:disable")
  return resp

@app.route('/about')
def about():
  return render_template("about.html")

@app.route('/solutions')
def solutions():
  return render_template("solutions.html", solutions=list_of_solutions)

@app.route('/create_paste')
def create_paste():
  return render_template("paste.html", page="create_paste")

@app.route('/import_paste')
def import_paste():
  return render_template("paste.html", page="import_paste")

@app.route('/upload_paste')
def upload_paste():
  return render_template("paste.html", page="upload_paste")

@app.route('/my_pastes')
def my_paste():
  return render_template("paste.html", page="my_pastes")

@app.route('/public_pastes')
def public_paste():
  return render_template("paste.html", page="public_pastes")

@app.route('/audit')
def audit():
  audit = Audit.query.all()
  return render_template("audit.html", audit=audit)

@app.route('/start_over')
def start_over():
  msg = "Restored to default state."
  res = helpers.initialize()

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

  helpers.set_mode(level)

  return render_template('index.html', msg = message)


@app.context_processor
def get_version():
  return dict(version=VERSION)

@app.before_request
def set_difficulty():
  mode_header = request.headers.get('X-DVGA-MODE', None)
  if mode_header:
    if mode_header == 'Expert':
      helpers.set_mode('hard')
    else:
      helpers.set_mode('easy')
  else:
    if session.get('difficulty') == None:
      helpers.set_mode('easy')

schema = graphene.Schema(query=Query, mutation=Mutations, directives=[ShowNetworkDirective, SkipDirective, DeprecatedDirective])

gql_middlew = [
  middleware.CostProtectionMiddleware(),
  middleware.DepthProtectionMiddleware(),
  middleware.IntrospectionMiddleware(),
  middleware.processMiddleware(),
  middleware.OpNameProtectionMiddleware()
]

igql_middlew = [
  middleware.IGQLProtectionMiddleware()
]

app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
  'graphql',
  schema=schema,
  middleware=gql_middlew,
  batch=True
))

app.add_url_rule('/graphiql', view_func=GraphQLView.as_view(
  'graphiql',
  schema = schema,
  graphiql = True,
  middleware = igql_middlew
))


