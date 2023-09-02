import graphene as g

from apps.api.graphql.utils import OrderDirection
from apps.carpool import services as api

from .types import CarType


class Query(g.ObjectType):
    cars = g.List(
        g.NonNull(CarType),
        required=True,
        description='Simply query for getting all the cars at once. No pagination is currently possible.',
        order=OrderDirection(required=False),
    )

    @staticmethod
    def resolve_cars(root, info, order=None):
        ascending_order = order is None or order == OrderDirection.ASCENDING
        return api.all_cars(ascending_order)
