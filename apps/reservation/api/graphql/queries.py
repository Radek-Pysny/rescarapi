import graphene as g

from apps.reservation import services as api

from .types import ReservationType


class ReservationConnection(g.Connection):
    class Meta:
        node = g.NonNull(ReservationType)

    class ReservationEdge(g.ObjectType):
        node = g.Field(ReservationType, required=True)
        cursor = g.String(required=True)

    edges = g.List(g.NonNull(ReservationEdge), required=True)
    total_count = g.Int(required=True)

    def resolve_total_count(root, info):
        """Total count of reservations."""

        return len(root.iterable)


class Query(g.ObjectType):
    reservation_by_request_id = g.Field(
        ReservationType,
        required=False,
        description='Retrieve single reservation by the given request ID iff it exists.',
        request_id=g.UUID(required=True),
    )

    @staticmethod
    def resolve_reservation_by_request_id(root, info, request_id):
        return api.fetch_reservation_by_request_id(request_id)

    reservations = g.ConnectionField(
        ReservationConnection,
        required=True,
        description='Retrieve all reservations at once.',
    )

    @staticmethod
    def resolve_reservations(root, info, **kwargs):
        # kwargs handles
        return api.fetch_reservations()


