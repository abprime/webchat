from rest_framework import serializers
from rooms.models import Room, Message


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['admin', 'name', 'members', 'moderators', 'id', 'protected']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['author', 'room', 'content', 'posted_at']
