from django.db import models as m
from django.utils.translation import gettext_lazy as _

from libs.models import BaseModel

from .validators import validate_car_id


class CarMake(BaseModel):
    name = m.CharField(
        null=False,
        max_length=50,
        verbose_name=_('car make name'),
        help_text=_('Simple name of the car make.'),
    )

    official_name = m.CharField(
        null=False,
        max_length=1000,
        verbose_name=_('car make official name'),
        help_text=_('Official name of the car make (including Ltd. or GmbH).'),
    )

    class Meta:
        verbose_name = _('car make')
        verbose_name_plural = _('car makes')

    def __repr__(self):
        return f'<CarMake {self.pk}/{self.name}>'

    def __str__(self):
        return self.name


class CarModel(BaseModel):
    make = m.ForeignKey(
        CarMake,
        null=False,
        on_delete=m.CASCADE,
        related_name='models',
        verbose_name=_('car make'),
        help_text=_('Make of the car model.'),
    )

    name = m.CharField(
        null=False,
        max_length=50,
        verbose_name=_('car model'),
        help_text=_('Model of a car.'),
    )

    class Meta:
        verbose_name = _('car model')
        verbose_name_plural = _('car models')

    def __repr__(self):
        return f'<CarModel {self.pk}/{self.name}>'

    def __str__(self):
        return f'{self.make.name} {self.name}'


class Car(BaseModel):
    model = m.ForeignKey(
        CarModel,
        null=False,
        on_delete=m.CASCADE,
        related_name='cars',
        verbose_name=_('car'),
        help_text=_('Model of the given car.'),
    )

    car_id = m.CharField(
        null=False,
        unique=True,
        max_length=50,
        validators=[validate_car_id],
        verbose_name=_('internal car ID'),
        help_text=_('Internal car ID that consists of a string with C-prefix and up to 10 decimal digits.'),
    )

    registration_number = m.CharField(
        null=False,
        max_length=8,
        verbose_name=_('car registration number'),
        help_text=_('Car registration number that consists from 8 characters with at least one digit.'),
    )

    class Meta:
        verbose_name = _('car')
        verbose_name_plural = _('cars')

    def __repr__(self):
        return f'<Car {self.pk}/{self.car_id}>'

    def __str__(self):
        return f'{self.car_id}'
