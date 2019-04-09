import graphene
from graphene_django_subscriptions.subscription import Subscription

from rooms.serializers import RoomSerializer, MessageSerializer


class RoomSubscription(Subscription):
    class Meta:
        serializer_class = RoomSerializer
        stream = 'rooms'
        description = 'Room subscription'


class MessageSubscription(Subscription):
    class Meta:
        serializer_class = MessageSerializer
        stream = 'messages'
        description = 'Message subscription'


class Subscription:
    room_subscription = RoomSubscription.Field()
    message_subscription = MessageSubscription.Field()
