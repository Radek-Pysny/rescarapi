import graphene as g

from apps.carpool.api.graphql.types import CarType
from apps.reservation.models import Reservation


class ReservationType(g.ObjectType):
    class Meta:
        interfaces = (g.Node,)
        model = Reservation

    id = g.ID(required=True)
    to_rent_at = g.DateTime(required=True)
    to_return_at = g.DateTime(required=True)
    duration_minutes = g.Int(required=True)
    request_id = g.UUID(required=False)
    client_name = g.String(required=True)
    car = g.Field(
        CarType,
        required=True,
    )

    def resolve_id(root: Reservation, info):
        return root.id

    def resolve_to_rent_at(root: Reservation, info):
        return root.to_return_at

    def resolve_to_return_at(root: Reservation, info):
        return root.to_return_at

    def resolve_duration_minutes(root: Reservation, info):
        return (root.to_return_at - root.to_rent_at).total_seconds() / 60

    def resolve_request_id(root: Reservation, info):
        return root.request_id

    def resolve_client_name(root: Reservation, info):
        return root.client_name
