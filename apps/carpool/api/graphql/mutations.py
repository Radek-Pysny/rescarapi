import graphene as g

from apps.carpool import services as api
from .types import CarType


class AddCarInput(g.InputObjectType):
    make = g.String(required=True)
    model = g.String(required=True)
    car_id = g.String(required=True)
    registration_number = g.String(required=True)


class AddCarMutation(g.Mutation):
    class Meta:
        name = 'AddCarPayload'

    class Arguments:
        input = AddCarInput(required=True)

    payload = g.Field(CarType)

    @classmethod
    def mutate(cls, root, info, input: AddCarInput):
        car = api.get_or_create_car(
            make=str(input.make),
            model=str(input.model),
            car_id=str(input.car_id),
            registration_number=str(input.registration_number),
        )
        return cls(payload=car)


class DeleteCarInput(g.InputObjectType):
    car_id = g.String(required=True)


class DeleteCarMutation(g.Mutation):
    class Meta:
        name = 'DeleteCarPayload'

    class Arguments:
        input = DeleteCarInput(required=True)

    payload = g.Field(CarType)

    @classmethod
    def mutate(cls, root, info, input: DeleteCarInput):
        car = api.delete_car(input.car_id)
        return cls(payload=car)


class UpdateCarInput(g.InputObjectType):
    car_id = g.String(required=True)
    make = g.String(required=False)
    model = g.String(required=False)
    registration_number = g.String(required=False)


class UpdateCarMutation(g.Mutation):
    class Meta:
        name = 'UpdateCarPayload'

    class Arguments:
        input = UpdateCarInput(required=True)

    payload = g.Field(CarType)

    @classmethod
    def mutate(cls, root, info, input: UpdateCarInput):
        kwargs = {
            k: v
            for k, v in (
                ('registration_number', input.registration_number),
                ('model_name',               input.model),
                ('make',                input.make),
            )
            if v is not None
        }
        car = api.update_car(car_id=str(input.car_id), **kwargs)
        return cls(payload=car)


class Mutation(g.ObjectType):
    add_car = AddCarMutation.Field()
    delete_car = DeleteCarMutation.Field()
    update_car = UpdateCarMutation.Field()
