import graphene
from graphene_django_subscriptions.subscription import Subscription

from users.serializers import UserSerializer


class UserSubscription(Subscription):
    class Meta:
        serializer_class = UserSerializer
        stream = 'users'
        description = 'User subscription'


class Subscription:
    user_subscription = UserSubscription.Field()
