"""Centralized definition of GraphQL schema (from possibly scattered query classes and mutations classes along
the project).
"""

import graphene

from apps.carpool.api.graphql.queries import Query as CarpoolQuery
from apps.carpool.api.graphql.mutations import Mutation as CarpoolMutation
from apps.reservation.api.graphql.queries import Query as ReservationQuery
from apps.reservation.api.graphql.mutations import Mutation as ReservationMutation


class Query(
    CarpoolQuery,
    ReservationQuery,
):
    pass


class Mutation(
    CarpoolMutation,
    ReservationMutation,
):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[],
)
