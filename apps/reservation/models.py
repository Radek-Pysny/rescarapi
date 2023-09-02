from datetime import timedelta
from django.db import models as m
from django.utils.translation import gettext_lazy as _

from libs.models import BaseModel
from apps.carpool.models import Car


class Reservation(BaseModel):
    to_rent_at = m.DateTimeField(
        null=False,
        verbose_name=_('to rent at'),
        help_text=_('Timestamp representing the time intent when a car shall be acquired from the rental.')
    )

    to_return_at = m.DateTimeField(
        null=False,
        verbose_name=_('to return at'),
        help_text=_('Timestamp representing time intent when a car shall be returned to the rental.'),
    )

    car = m.ForeignKey(
        Car,
        null=False,
        on_delete=m.CASCADE,
        related_name='reservations',
        verbose_name=_('car for rent'),
        help_text=_('The car that has been pre-selected for the rental'),
    )

    request_id = m.UUIDField(
        null=True,
        verbose_name=_('request ID'),
        help_text=_('ID of request that is internally generated as soon as reservation request is pending.'),
    )

    client_name = m.CharField(
        null=False,
        max_length=100,
        verbose_name=_('client name'),
        help_text=_('Name of the client who reserved the car rental.'),
    )

    class Meta:
        verbose_name = _('reservation')
        verbose_name_plural = _('reservations')

    def duration(self) -> timedelta:
        return self.to_return_at - self.to_rent_at
