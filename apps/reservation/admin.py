from datetime import timedelta
from django.db.models import F
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from libs.admin.filters import TimeIntervalFilter
from .models import Reservation


class ReservationDuration(admin.SimpleListFilter):
    title = _('duration')
    parameter_name = 'xyz'

    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    TWO_WEEKS = '2 weeks'
    LONGER = 'longer'

    def lookups(self, request, model_admin):
        return [
            (self.HOUR, _('X <= hour')),
            (self.DAY, _('hour < X <= day')),
            (self.WEEK, _('day < X <= week')),
            (self.TWO_WEEKS, _('week < X <= 2 weeks')),
            (self.LONGER, _('2 weeks < X'))
        ]

    def queryset(self, request, queryset):
        selection = self.value()

        limit = (None, None)
        match selection:
            case self.HOUR:
                limit = (None, timedelta(hours=1))
            case self.DAY:
                limit = (timedelta(hours=1), timedelta(days=1))
            case self.WEEK:
                limit = (timedelta(days=1), timedelta(weeks=1))
            case self.TWO_WEEKS:
                limit = (timedelta(weeks=1), timedelta(weeks=2))
            case self.LONGER:
                limit = (timedelta(weeks=2), None)

        kwargs = {}
        if gt := limit[0]:
            kwargs['rent_duration__gt'] = gt
        if le := limit[1]:
            kwargs['rent_duration__lte'] = le

        return queryset.annotate(rent_duration=F('to_return_at')-F('to_rent_at')).filter(**kwargs)


class ReservationToRentAtFilter(TimeIntervalFilter):
    title = _('to rent at')
    parameter_name = 'to_rent_at'


class ReservationToReturnAtFilter(TimeIntervalFilter):
    title = _('to return at')
    parameter_name = 'to_return_at'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    model = Reservation

    list_display = (
        'id', 'request_id', 'car', 'get_model', 'to_rent_at', 'to_return_at', 'get_duration', 'client_name',
    )

    list_filter = (
        'car',
        'car__model',
        ReservationToRentAtFilter,
        ReservationToReturnAtFilter,
        ReservationDuration,
    )

    @admin.display(description=_('duration'))
    def get_duration(self, obj: Reservation):
        return obj.duration()

    @admin.display(description=_('model_name'))
    def get_model(self, obj: Reservation):
        return obj.car.model
