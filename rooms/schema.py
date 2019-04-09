import graphene
import graphql_jwt

from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, user_passes_test

from rooms.models import Room, Message


class RoomType(DjangoObjectType):
    id = graphene.Int(source='pk')

    class Meta:
        model = Room
        only_fields = ['admin', 'moderators', 'members', 'protected', 'name', 'messages', 'id']


class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        exclude_fields = ['pk', 'id']


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
