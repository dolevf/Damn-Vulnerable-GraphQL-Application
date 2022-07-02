from unicodedata import name
from graphql import GraphQLArgument, GraphQLNonNull, GraphQLString
from graphql.type.directives import GraphQLDirective, DirectiveLocation, GraphQLDeprecatedDirective, GraphQLSkipDirective

ShowNetworkDirective = GraphQLDirective(
    name="show_network",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "style": GraphQLArgument(
            GraphQLNonNull(GraphQLString)
        )
    },
    description="Displays the network associated with an IP Address (CIDR or Net)."
)

Auth = GraphQLDirective(
    name="auth",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "requires": GraphQLArgument(
            GraphQLNonNull(GraphQLString)
        )
    },
    description="Determines what type of user role is allowed to view a particular field"
)

DeprecatedDirective = GraphQLDeprecatedDirective
SkipDirective = GraphQLSkipDirective