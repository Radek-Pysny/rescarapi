from django.contrib import admin
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta, MO, SU


class TimeIntervalFilter(admin.SimpleListFilter):
    title = ''
    parameter_name = ''

    PAST = 'past'
    TODAY = 'today'
    TOMORROW = 'tomorrow'
    THIS_WEEK = 'this week'
    THIS_MONTH = 'this month'
    FUTURE = 'future'

    def lookups(self, request, model_admin):
        return [
            (self.PAST, _('past')),
            (self.TODAY, _('today')),
            (self.TOMORROW, _('tomorrow')),
            (self.THIS_WEEK, _('this week')),
            (self.THIS_MONTH, _('this month')),
            (self.FUTURE, _('future')),
        ]

    def queryset(self, request, queryset):
        selection = self.value()
        today = now() + relativedelta(hour=0, minute=0, second=0, microsecond=0)

        limits = (None, None)
        match selection:
            case self.PAST:
                limits = (None, today)
            case self.TODAY:
                limits = (today, today + relativedelta(days=+1))
            case self.TOMORROW:
                limits = (today + relativedelta(days=+1), today + relativedelta(days=+2))
            case self.THIS_WEEK:
                limits = (today + relativedelta(weekday=MO(-1)), today + relativedelta(weekday=SU))
            case self.THIS_MONTH:
                limits = (today + relativedelta(day=1), today + relativedelta(months=+1) + relativedelta(day=1))
            case self.FUTURE:
                limits = (today, None)

        kwargs = {}
        if start := limits[0]:
            kwargs[self.parameter_name + '__gte'] = start
        if end := limits[1]:
            kwargs[self.parameter_name + '__lt'] = end

        return queryset.filter(**kwargs)
