import graphene
import graphql_jwt

from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ['username', 'email', 'is_staff']


class RegisterMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, username, password, email):
        if not User.objects.filter(username=username, email=email).exists():
            new_user = User.objects.create(username=username, email=email)
            new_user.set_password(password)
            new_user.save()

            return RegisterMutation(user=new_user)

        return RegisterMutation(user=None)


class Query:

    me = graphene.Field(UserType, token=graphene.String(required=True))

    @login_required
    def resolve_me(self, info, **kwargs):
        return info.context.user


class Mutation:

    register = RegisterMutation.Field()

    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Subscription:
    pass
