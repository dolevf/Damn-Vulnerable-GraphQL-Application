import os
import re
import string
import config


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth

from dvga.helpers import initialize
from dvga.helpers import level_is_easy
from dvga.helpers import level_is_hard

from secrets import choice


app = Flask(__name__, static_folder="static/")
app.schema = None
chrset = string.ascii_lowercase + string.digits

# Weakened deliberately to allow for JWT bruteforce 
app.secret_key = ''.join([choice(chrset) for _ in range(6)]) 
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["UPLOAD_FOLDER"] = config.WEB_UPLOADDIR

db = SQLAlchemy(app)
auth = GraphQLAuth(app)


if __name__ == '__main__':
    initialize()
    from dvga.schema import *
    from dvga.routes import *

    app.schema = graphene.Schema(query=Query, mutation=Mutations)
    
    auth = GraphQLAuth(app)

    gql_middlew = [
        CostProtectionMiddleware(),
        DepthProtectionMiddleware(),
        IntrospectionMiddleware(),
        ProcessMiddleware(),
        OpNameProtectionMiddleware(),
    ]

    igql_middlew = [IGQLProtectionMiddleware()]


    app.add_url_rule('/graphql', 
                     view_func=GraphQLView.as_view(
                         'graphql',
                         schema=        app.schema,
                         middleware=    gql_middlew,
                         batch=         True
                     )
    )

    app.add_url_rule('/graphiql', 
                     view_func= GraphQLView.as_view('graphiql',
                         schema=        app.schema,
                         graphiql=      True,
                         middleware=    igql_middlew,
                         batch=         True
                     )
    )
    app.run(debug=      config.WEB_DEBUG,
            host=       config.WEB_HOST,
            port=       config.WEB_PORT,
            threaded=   True,
            use_evalex= False)