import graphene
import graphql_jwt
import logging
import json
import time

import redis
from redis.client import PubSubWorkerThread
from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, user_passes_test
from rx import Observable, Observer
from rx.subjects import Subject
from graphql_jwt import shortcuts
from django.conf import settings

from rooms.models import Room, Message

from chat.redis_client import redis_client


logger = logging.getLogger(__name__)


class RoomType(DjangoObjectType):
    id = graphene.Int(source='pk')

    class Meta:
        model = Room
        only_fields = ['admin', 'moderators', 'members', 'protected', 'name', 'messages', 'id']


class MessageType(DjangoObjectType):
    id = graphene.Int(source='pk')

    class Meta:
        model = Message


class CreateRoomMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        name = graphene.String(required=True)
        password = graphene.String(required=False)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, token, name, password):
        if info.context.user:
            room = Room.objects.create(
                admin=info.context.user,
                name=name,
                protected=password is not None,
                password=password
            )

            return CreateRoomMutation(room=room)

        return CreateRoomMutation(room=None)


class PostMessageMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        room_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, token, room_id, content):
        try:
            room = Room.objects.get(pk=room_id)
            user = room.members.get(pk=info.context.user.pk)  # testing if user can post messages
            message = Message.objects.create(author=user, content=content, room=room)

            redis_client.publish(f'room-{room_id}', json.dumps({
                'type': 'NEW_MESSAGE',
                'pk': message.pk
            }))

            return PostMessageMutation(message=message)

        except Exception:
            return PostMessageMutation(message=None)


class EnterRoomMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        room_id = graphene.Int(required=True)
        password = graphene.String(required=False)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, token, room_id, password):
        try:
            room = Room.objects.get(pk=room_id)

            if not room.members.filter(pk=info.context.user.pk).exists():
                room.members.add(info.context.user)
                room.save(update_fields=['members'])

            return EnterRoomMutation(room=room)

        except Exception:
            return EnterRoomMutation(room=None)


class Query:

    rooms = graphene.List(RoomType, token=graphene.String(required=True))
    my_rooms = graphene.List(RoomType, token=graphene.String(required=True))
    room = graphene.Field(RoomType, token=graphene.String(required=True), room_id=graphene.Int(required=True))

    @login_required
    def resolve_rooms(self, info, **kwargs):
        if info.context.user:
            return Room.objects.all()

        return None

    @login_required
    def resolve_room(self, info, **kwargs):
        try:
            room_id = kwargs.get('room_id')
            room = Room.objects.get(pk=room_id)

            user = room.members.get(pk=info.context.user.pk)

            return room

        except Exception:
            return None

    @login_required
    def resolve_my_rooms(self, info, **kwargs):
        if info.context.user:
            return info.context.user.rooms.all()

        return None


class Mutation:
    create_room = CreateRoomMutation.Field()
    enter_room = EnterRoomMutation.Field()
    post_message = PostMessageMutation.Field()


class Subscription:
    new_message = graphene.Field(MessageType,
                                 token=graphene.String(required=True),
                                 room_id=graphene.Int(required=True))

    def resolve_new_message(self, info, token, room_id, **kwargs):
        user = shortcuts.get_user_by_token(token)
        user_id = user.pk

        room = Room.objects.get(pk=room_id)
        room.members.get(pk=user.pk)

        source = Subject()

        def handler(event):
            if event is not None:
                source.on_next(event)

        pubsub = redis_client.pubsub()
        pubsub.subscribe(**{f'room-{room_id}': handler})

        pubsub.run_in_thread(sleep_time=0.001)

        return source.filter(lambda event: isinstance(event['data'], bytes))\
                     .map(lambda event: json.loads(event['data'].decode()))\
                     .filter(lambda event: event['type'] == 'NEW_MESSAGE')\
                     .map(lambda event: Message.objects.get(pk=event['pk']))\
                     .filter(lambda message: message.room.pk == room_id)
