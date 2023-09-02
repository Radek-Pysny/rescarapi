import graphene as g
from graphene_django import DjangoObjectType

from apps.carpool.models import Car


class CarType(DjangoObjectType):
    class Meta:
        name = "Car"
        model = Car
        only_fields = ['car_id', 'registration_number']

    make = g.String(required=True)
    model = g.String(required=True)

    @staticmethod
    def resolve_make(parent: Car, info) -> str:
        return parent.model.make.name

    @staticmethod
    def resolve_model(parent: Car, info) -> str:
        return parent.model.name
