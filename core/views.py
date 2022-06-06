import graphene

from core import (
  security,
  helpers,
  middleware
)
from core.directives import *
from core.models import (
  Owner,
  Paste,
  User,
  Audit
)
from core.view_override import (
  OverriddenView,
  GeventSubscriptionServerCustom,
  format_custom_error
)
from db.solutions import solutions as list_of_solutions
from rx.subjects import Subject
from flask import (
  request,
  render_template,
  make_response,
  session
)
from flask_sockets import Sockets
from graphql.backend import GraphQLCoreBackend
from sqlalchemy import event, text
from graphene_sqlalchemy import SQLAlchemyObjectType

from app import app, db

from version import VERSION
from config import WEB_HOST, WEB_PORT

# SQLAlchemy Types
class UserObject(SQLAlchemyObjectType):
  class Meta:
    model = User
    exclude_fields = ('password',)

  username = graphene.String(capitalize=graphene.Boolean())

  @staticmethod
  def resolve_username(self, info, **kwargs):
    if kwargs.get('capitalize'):
      return self.username.capitalize()
    return self.username

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

class AuditObject(SQLAlchemyObjectType):
  class Meta:
    model = Audit

class UserInput(graphene.InputObjectType):
  username = graphene.String(required=True)
  password = graphene.String(required=True)

class CreateUser(graphene.Mutation):
  class Arguments:
    user_data = UserInput(required=True)

  user = graphene.Field(lambda:UserObject)

  def mutate(root, info, user_data=None):
    user_obj = User.create_user(
      username=user_data.username,
      password=user_data.password
    )

    Audit.create_audit_entry(info)

    return CreateUser(user=user_obj)

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

class EditPaste(graphene.Mutation):
    paste = graphene.Field(lambda:PasteObject)

    class Arguments:
      id = graphene.Int()
      title = graphene.String(required=False)
      content = graphene.String(required=False)

    def mutate(self, info, id, title=None, content=None):
      paste_obj = Paste.query.filter_by(id=id).first()

      if title == None:
        title = paste_obj.title
      if content == None:
        content = paste_obj.content

      Paste.query.filter_by(id=id).update(dict(title=title, content=content))
      paste_obj = Paste.query.filter_by(id=id).first()

      db.session.commit()

      Audit.create_audit_entry(info)

      return EditPaste(paste=paste_obj)

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
  edit_paste = EditPaste.Field()
  delete_paste = DeletePaste.Field()
  upload_paste = UploadPaste.Field()
  import_paste = ImportPaste.Field()
  create_user = CreateUser.Field()

global_event = Subject()

@event.listens_for(Paste, 'after_insert')
def new_paste(mapper,cconnection,target):
  global_event.on_next(target)

class Subscription(graphene.ObjectType):
  paste = graphene.Field(PasteObject, id=graphene.Int(), title=graphene.String())

  def resolve_paste(self, info):
    return global_event.map(lambda i: i)

class SearchResult(graphene.Union):
  class Meta:
    types = (PasteObject, UserObject)

class Query(graphene.ObjectType):
  pastes = graphene.List(PasteObject, public=graphene.Boolean(), limit=graphene.Int(), filter=graphene.String())
  paste = graphene.Field(PasteObject, id=graphene.Int(), title=graphene.String())
  system_update = graphene.String()
  system_diagnostics = graphene.String(username=graphene.String(), password=graphene.String(), cmd=graphene.String())
  system_debug = graphene.String(arg=graphene.String())
  system_health = graphene.String()
  users = graphene.List(UserObject, id=graphene.Int())
  read_and_burn = graphene.Field(PasteObject, id=graphene.Int())
  search = graphene.List(SearchResult, keyword=graphene.String())
  audits = graphene.List(AuditObject)

  def resolve_search(self, info, keyword=None):
    Audit.create_audit_entry(info)
    items = []
    if keyword:
      search = "%{}%".format(keyword)
      queryset1 = Paste.query.filter(Paste.title.like(search))
      items.extend(queryset1)
      queryset2 = User.query.filter(User.username.like(search))
      items.extend(queryset2)
    else:
      queryset1 = Paste.query.all()
      items.extend(queryset1)
      queryset2 = User.query.all()
      items.extend(queryset2)
    return items

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
      helpers.run_cmd("uptime | awk -F': ' '{print $2}' | awk -F',' '{print $1}'")
    )

  def resolve_users(self, info, id=None):
    query = UserObject.get_query(info)
    Audit.create_audit_entry(info)
    if id:
      result = query.filter_by(id=id)
    else:
      result = query

    return result

  def resolve_audits(self, info):
    query = Audit.query.all()
    Audit.create_audit_entry(info)
    return query

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
  audit = Audit.query.order_by(Audit.timestamp.desc())
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
def get_difficulty():
  level = None
  if helpers.is_level_easy():
    level = 'easy'
  else:
    level = 'hard'
  return dict(difficulty=level)

@app.context_processor
def get_server_info():
  return dict(version=VERSION, host=WEB_HOST, port=WEB_PORT)


@app.before_request
def set_difficulty():
  mode_header = request.headers.get('X-DVGA-MODE', None)
  if mode_header:
    if mode_header == 'Expert':
      helpers.set_mode('hard')
    else:
      helpers.set_mode('easy')

schema = graphene.Schema(query=Query, mutation=Mutations, subscription=Subscription, directives=[ShowNetworkDirective, SkipDirective, DeprecatedDirective])

subscription_server = GeventSubscriptionServerCustom(schema)

sockets = Sockets(app)

@sockets.route('/subscriptions')
def echo_socket(ws):

  subscription_server.handle(ws)

  return []


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

class CustomBackend(GraphQLCoreBackend):
    def __init__(self, executor=None):
        super().__init__(executor)
        self.execute_params['allow_subscriptions'] = True

app.add_url_rule('/graphql', view_func=OverriddenView.as_view(
  'graphql',
  schema=schema,
  middleware=gql_middlew,
  backend=CustomBackend(),
  batch=True
))

app.add_url_rule('/graphiql', view_func=OverriddenView.as_view(
  'graphiql',
  schema = schema,
  backend=CustomBackend(),
  graphiql = True,
  middleware = igql_middlew,
  format_error=format_custom_error
))


