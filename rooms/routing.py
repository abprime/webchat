from graphene_django_subscriptions.consumers import GraphqlAPIDemultiplexer
from channels.routing import route_class
from rooms.subscriptions import RoomSubscription, MessageSubscription


class RoomsDemultiplexer(GraphqlAPIDemultiplexer):
    consumers = {
        'rooms': RoomSubscription.get_binding().consumer,
        'messages': MessageSubscription.get_binding().consumer
    }


app_routing = [
    route_class(RoomsDemultiplexer)
]
