from graphene_django_subscriptions.consumers import GraphqlAPIDemultiplexer
from channels.routing import route_class
from users.subscriptions import UserSubscription


class UsersDemultiplexer(GraphqlAPIDemultiplexer):
    consumers = {
        'users': UserSubscription.get_binding().consumer,
    }


app_routing = [
    route_class(UsersDemultiplexer)
]
