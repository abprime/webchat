import graphene

from users.schema import Query as UsersQuery, Mutation as UsersMutation
from rooms.schema import Query as RoomsQuery, Mutation as RoomsMutation

from users.subscriptions import Subscription as UserSubscription
from rooms.subscriptions import Subscription as RoomSubscription


class Query(graphene.ObjectType, UsersQuery, RoomsQuery):
    pass


class Mutation(graphene.ObjectType, UsersMutation, RoomsMutation):
    pass


class Subscription(graphene.ObjectType, UserSubscription, RoomSubscription):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
