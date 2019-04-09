import graphene

from users.schema import Query as UsersQuery, Mutation as UsersMutation, Subscription as UsersSubscription
from rooms.schema import Query as RoomsQuery, Mutation as RoomsMutation, Subscription as RoomsSubscription


class Query(graphene.ObjectType, UsersQuery, RoomsQuery):
    pass


class Mutation(graphene.ObjectType, UsersMutation, RoomsMutation):
    pass


class Subscription(graphene.ObjectType, UsersSubscription, RoomsSubscription):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
