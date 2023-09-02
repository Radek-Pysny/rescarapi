import structlog
import uuid
from django.db.models import Q, OuterRef, Exists
from django.utils.timezone import now, datetime, timedelta

from apps.carpool.models import Car
from libs.models.abstract import date_updated
from .errors import ReservationInternalError, ReservationFailedAttemptError, ReservationNoCarAvailableError
from .models import Reservation


log = structlog.get_logger()


def _during_that_time_filter(to_rent_at: datetime, to_return_at: datetime) -> Q:
    """Construct filter for checking that any reservation in that time already exists."""

    return (
        # reservations that are completely within requested reservation (or equals)
        Q(to_rent_at__gte=to_rent_at, to_return_at__lte=to_return_at) |
        # reservations that collide with requested reservations start
        Q(to_rent_at__lt=to_rent_at, to_return_at__gt=to_rent_at) |
        # reservations that collide with requested reservation end
        Q(to_rent_at__lt=to_return_at, to_return_at__gt=to_return_at)
    )


def count_reservations_for_car(
        car: Car,
        to_rent_at: datetime,
        to_return_at: datetime,
) -> int:
    """Count reservations for the car in the given interval."""

    time_filter = _during_that_time_filter(to_rent_at=to_rent_at, to_return_at=to_return_at)
    return Reservation.objects.filter(time_filter, car=car).count()


def make_reservation(
        request_id: uuid.UUID,
        to_rent_at: datetime,
        duration: timedelta,
        dry_run: bool = False,
) -> Reservation:
    """Try to make a reservation."""

    limit = 10
    to_return_at = to_rent_at + duration

    _log = log.bind(ts=now(), request_id=request_id)
    _log.info('request_reservation', to_rent_at=to_rent_at, to_return_at=to_return_at, duration=duration)

    no_reservation_filter = ~Exists(
        Reservation.objects.filter(
            _during_that_time_filter(to_rent_at=to_rent_at, to_return_at=to_return_at),
            car=OuterRef('pk'),
        )
    )
    available_cars = list(Car.objects.filter(no_reservation_filter).all()[:limit + 1])

    if not len(available_cars):
        _log.warn('no car available')
        raise ReservationNoCarAvailableError

    for trial, available_car in enumerate(available_cars, start=1):
        reservation = Reservation(
            to_rent_at=to_rent_at,
            to_return_at=to_return_at,
            car=available_car,
        )

        if dry_run:
            return reservation

        reservation.save()

        # check that no other reservation was done for the same in the meanwhile
        count = count_reservations_for_car(car=available_car, to_rent_at=to_rent_at, to_return_at=to_return_at)
        match count:
            case 0:
                _log.error('not able to find own temporary reservation', trial=trial, count=len(available_cars))
                raise ReservationInternalError

            case 1:
                # finish the reservation by saving its request ID
                try:
                    reservation.request_id = request_id
                    reservation.save(update_fields=['request_id', date_updated])
                except Exception:
                    raise ReservationInternalError
                else:
                    return reservation

            case _:
                reservation.delete()

    count = len(available_cars)
    if count > limit:
        count = f'>{count}'
    _log.warn(f'failed to reserve with {count} available cars')
    raise ReservationFailedAttemptError


def fetch_reservations():
    return Reservation.objects.all()


def fetch_reservation_by_request_id(request_id):
    try:
        return Reservation.objects.get(request_id=request_id)
    except Reservation.DoesNotExist:
        return None
