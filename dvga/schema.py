import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy import SQLAlchemyConnectionField

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import make_response
from flask import session
from flask_graphql import GraphQLView
from flask_graphql_auth import AuthInfoField
from flask_graphql_auth import GraphQLAuth
from flask_graphql_auth import get_jwt_identity
from flask_graphql_auth import create_access_token
from flask_graphql_auth import create_refresh_token
from flask_graphql_auth import query_header_jwt_required
from flask_graphql_auth import mutation_jwt_refresh_token_required
from flask_graphql_auth import mutation_jwt_required

from app import app
from app import db

from .security import *
from .helpers import *
from .models import *

##############################################################################
# Types
##############################################################################

class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node, )

class PasteObject(SQLAlchemyObjectType):
    p_id = graphene.String(source='id')
    class Meta:
        model = Paste
        interfaces = (graphene.relay.Node, )


##############################################################################
# Queries
##############################################################################
class Query(graphene.ObjectType):
    node =               graphene.relay.Node.Field()
    users =              graphene.List(UserObject,)
    admins =             graphene.List(UserObject,)
    user =               graphene.List(UserObject,   username=  graphene.String())
    pastes =             graphene.List(PasteObject,  username=  graphene.String())
    public_pastes =      graphene.List(PasteObject,  username=  graphene.String())
    paste =              graphene.Field(PasteObject, p_id=      graphene.Int())
    read_and_burn =      graphene.Field(PasteObject, p_id=      graphene.Int())
    system_update =      graphene.String()
    system_health =      graphene.String()
    system_diagnostics = graphene.String(username=  graphene.String(), 
                                         password=  graphene.String(), 
                                         cmd=       graphene.String()) 

    def resolve_user(self, info, username):
        user = User.query.filter_by(username=username).first()
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        
        if user:
            return user
        else:
            return None

    # Deliberately serving all pastes if no username is given
    def resolve_public_pastes(self, info):
        query = PasteObject.get_query(info)
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return query.filter_by(public=True, burn=False).order_by(Paste.id.desc())

    # Deliberately serving all pastes if no username is given
    def resolve_pastes(self, info, username='admin'):
        query = PasteObject.get_query(info)
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        
        if level_is_easy():

            # Deliberately doing raw injectable SQL here 
            query = """                                 \
                        SELECT *                        \
                        FROM pastes                     \
                        LEFT JOIN users                 \
                        ON pastes.user_id = users.id    \
                        WHERE users.username = ?        \
                        AND pastes.burn = FALSE         \
                        ORDER BY pastes.id              \
                        DESC                            \
                   """
                
            result_set = []
            
            
            # Force update of all objects. Useful after repeated use of the moderate feature
            db.session.flush()

            for r in db.engine.execute(query, username): 
                # Deliberately rebuilding the related User object here 
                # which introduces an access control vuln to the user's password
         
                p =             Paste()
                p.id =          r[0]
                p.title =       r[1]
                p.content =     r[2]
                p.public =      r[3]
                p.user_id =     r[8]
                p.user =        User(username=r[9], password=r[10], roles=r[11])
                p.user_agent =  r[4]
                p.ip_addr =     r[5]
                         
                result_set.append(p)

            return result_set

        elif level_is_hard:
            username = 'user' # Removing the defaulting vulnerability
            query = PasteObject.get_query(info)
            user = User.query.filter_by(username=username).first()
            Audit.create_audit_entry(gqloperation=get_opname(info.operation))
            # Removin SQL injection condition
            return query.filter_by(public=True, burn=False, user_id=user.id).order_by(Paste.id.desc())

    def resolve_paste(self, info, p_id):
        query = PasteObject.get_query(info)
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return query.filter_by(id=p_id, burn=False).first()

    def resolve_system_update(self, info):
        security.simulate_load()
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return 'no updates available'

    def resolve_system_diagnostics(self, info, username, password, cmd='whoami'):
        user = User.query.filter_by(usernamme=username).first()
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        if session.get('authenticated') and 'admin' in session.get('current_user_roles') :
            output = f'{cmd}: command not found'
            if security.allowed_cmds(cmd):
                output = run_cmd(cmd)
            return output
        return msg

    def resolve_read_and_burn(self, info, p_id):
        result = Paste.query.filter_by(id=p_id, burn=True).first()
        Paste.query.filter_by(id=p_id, burn=True).delete()
        db.session.commit()
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return result

    def resolve_system_health(self, info):
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return 'System Load: {}'.format(run_cmd("uptime | awk '{print $10, $11, $12}'"))

##############################################################################
# Mutations
##############################################################################


# Authentication
class AuthenticateUser(graphene.Mutation):
    access_token =  graphene.String()

    class Arguments:
        username =  graphene.String()
        password =  graphene.String()
    
    def mutate(self, info, username, password):
        user = User.query.filter_by(username=username,password=password).first()
        if not user:
            raise Exception('Authenication Failure : User is not registered')

        return AuthenticateUser(access_token=make_hard_token(user))


# Users
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserObject)
        
    class Arguments:
        username =  graphene.String(required=True)
        password =  graphene.String(required=True)
        roles =     graphene.String(required=True)
        
    def mutate(self, info, username, password , roles):
        found_user = User.query.filter_by(username=username).first()
        if user:
                return CreateUser(user=found_user)
    
        new_user = User.create_user(
                                username=username,
                                password=password,
                                roles=roles,
                        )
        return CreateUser(user=new_user)

# Pastes
class CreatePaste(graphene.Mutation):
    title =       graphene.String()
    content =     graphene.String()
    public =      graphene.Boolean()
    paste =       graphene.Field(lambda:PasteObject)
    burn =        graphene.Boolean()

    class Arguments:
        username = graphene.String()
        title =   graphene.String()
        content = graphene.String()
        public =  graphene.Boolean(required=False, default_value=True)
        burn =    graphene.Boolean(required=False, default_value=False)

    def mutate(self, info, title, content, public, burn, username):
        user = User.query.filter_by(username=username).first()
        paste_obj = Paste.create_paste(
                        title=      title,
                        content=    content, 
                        public=     public, 
                        burn=       burn,
                        user_id=    user.id, 
                        user=       user, 
                        ip_addr=    request.remote_addr,
                        user_agent= request.headers.get('User-Agent', '')
                    )
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))
        return CreatePaste(paste=paste_obj)

class DeletePaste(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        title = graphene.String()

    def mutate(self, info, title):
        Paste.query.filter_by(title=title).delete()
        db.session.commit()

        Audit.create_audit_entry(gqloperation=get_opname(info.operation))

        return DeletePaste(ok=True)

class UploadPaste(graphene.Mutation):
    content =       graphene.String()
    filename =      graphene.String()

    class Arguments:
        content =   graphene.String(required=True)
        filename =  graphene.String(required=True)

    result = graphene.String()

    def mutate(self, info, filename, content, username):
        result = save_file(filename, content)
        user = User.query.filter_by(username=username).first()

        Paste.create_paste(
                title=      'Imported Paste from File - {}'.format(generate_uuid()),
                content=    content, public=False, burn=False,
                user_id=    user.id, user=user, ip_addr=request.remote_addr,
                user_agent= request.headers.get('User-Agent', '')
        )

        Audit.create_audit_entry(gqloperation=get_opname(info.operation))

        return UploadPaste(result=result)

class ImportPaste(graphene.Mutation):
    result = graphene.String()

    class Arguments:
        host =     graphene.String(required=True)
        port =     graphene.Int(required=False)
        path =     graphene.String(required=True)
        scheme =   graphene.String(required=True)

    # Deliberately setting default user as "admin" for importing pastes
    def mutate(self, info, host='pastebin.com', port=443, path='/', scheme="http", username="admin"):
        url = security.strip_dangerous_characters(f"{scheme}://{host}:{port}{path}")
        cmd = run_cmd(f'curl --insecure {url}')

        user = User.query.filter_by(name=username).first()
        Paste.create_paste(
            title='Imported Paste from URL - {}'.format(generate_uuid()),
            content=cmd, 
            public=False, 
            burn=False,
            user_id=user.id, 
            user=user, 
            ip_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        Audit.create_audit_entry(gqloperation=get_opname(info.operation))

        return ImportPaste(result=cmd)


class ModeratePaste(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)
        visibility = graphene.Boolean(required=True)
        
    def mutate(self, info, id, visibility):
        updated_paste = Paste.query.filter_by(id=id).first()
        updated_paste.public = visibility
        db.session.commit()
        
        ok = True
        Audit.create_audit_entry(gqloperation=get_opname(info.operation))   
        return ModeratePaste(ok=True)

class Mutations(graphene.ObjectType):
    # Authentication mutations
    login_verify = AuthenticateUser.Field()
    
    # User mutations
    add_new_user = CreateUser.Field()

    # Paste mutations
    create_paste =      CreatePaste.Field()
    delete_paste =      DeletePaste.Field()
    upload_paste =      UploadPaste.Field()
    import_paste =      ImportPaste.Field()
    moderate_paste =    ModeratePaste.Field()