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

DeprecatedDirective = GraphQLDeprecatedDirective
SkipDirective = GraphQLSkipDirective