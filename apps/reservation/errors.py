class ReservationError(ValueError):
    """Base exception/error type for reservation app."""


class ReservationNoCarAvailableError(ReservationError):
    """Reservation error - no available car."""

    def __init__(self, *args):
        if len(args):
            super().__init__(*args)

        super().__init__('no car available for reservation')


class ReservationFailedAttemptError(ReservationError):
    """Reservation error - failed trials for reservation on up to limit number of available cars."""

    def __init__(self, *args):
        if len(args):
            super().__init__(*args)

        super().__init__('all trials for reservation failed')


class ReservationInternalError(ReservationError):
    """Inconsistent database status."""

    def __init__(self, *args):
        if len(args):
            super().__init__(*args)

        super().__init__('internal error during reservation')
