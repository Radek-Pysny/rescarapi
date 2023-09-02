import graphene as g
from datetime import datetime, timedelta
from uuid import uuid4

from apps.reservation import services as api
from .types import ReservationType


class ReserveInput(g.InputObjectType):
    to_rent_at = g.DateTime(require=True)
    duration_minutes = g.Int(required=True)


class ReserveMutation(g.Mutation):
    class Meta:
        name = 'ReservePayload'

    class Arguments:
        input = ReserveInput(required=True)

    payload = g.Field(ReservationType)

    @classmethod
    def mutate(cls, root, info, input: ReserveInput):
        to_rent_at = input.to_rent_at
        request_id = uuid4()
        reservation = api.make_reservation(
            request_id=request_id,
            to_rent_at=to_rent_at,
            duration=timedelta(minutes=float(input.duration_minutes)),
            dry_run=False,
        )
        return cls(payload=reservation)


class Mutation(g.ObjectType):
    reserve = ReserveMutation.Field()
