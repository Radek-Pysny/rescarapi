"""Definition of URLs for Rest API end-points and GraphQL end-point(s).
"""

from django.conf import settings
from django.urls import path
from graphene_django.views import GraphQLView

app_name = 'api'

urlpatterns = [
    # GraphQL
    path('gql', GraphQLView.as_view(graphiql=False)),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [
        path('giql', GraphQLView.as_view(graphiql=True)),
    ]
