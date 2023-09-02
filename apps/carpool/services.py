import structlog
from django.db.models import Q
from django.utils.timezone import now

from libs.models.abstract import date_updated
from libs.text_utils import preprocess_for_comparison
from .errors import CarpoolAlreadyExistsError, CarpoolInconsistentError, CarpoolNotFoundError
from .models import CarMake, CarModel, Car
from .validators import validate_car_id


log = structlog.get_logger()


def get_or_create_car_make(
        name: str,
        official_name: str | None = None,
        raise_on_existing: bool = False,
) -> CarMake:
    """Retrieve CarMake object from DB or create a new one."""

    if not name:
        raise ValueError('empty name')

    q = Q(name__iexact=preprocess_for_comparison(name))
    if official_name:
        q |= Q(official_name__iexact=preprocess_for_comparison(official_name))

    if not official_name:
        official_name = name

    if CarMake.objects.filter(q).count():
        if raise_on_existing:
            raise CarpoolAlreadyExistsError(make_name=name)

        return CarMake.objects.get(q)

    return CarMake.objects.create(
        name=name,
        official_name=official_name,
    )


def get_or_create_car_model(
        make: CarMake | str,
        model_name: str,
        raise_on_existing: bool = False,
) -> CarModel:
    """Retrieve CarModel object from DB or create a new one. If the given make and/or model_name does not exist,
    one is created.
    """

    if isinstance(make, str):
        make = get_or_create_car_make(make, raise_on_existing=False)

    q = Q(name__iexact=preprocess_for_comparison(model_name), make=make)

    if CarModel.objects.filter(q).count():
        if raise_on_existing:
            raise CarpoolAlreadyExistsError(model_name=model_name)

        return CarModel.objects.get(q)

    return CarModel.objects.create(
        make=make,
        name=model_name,
    )


def get_or_create_car(
        make: CarMake | str,
        model: CarModel | str,
        car_id: str,
        registration_number: str,
        raise_on_existing: bool = False,
) -> Car:
    """Retrieve Car object from DB or create a new one. Model and make can be automatically created on demand."""

    validate_car_id(car_id)

    if isinstance(make, str):
        make = get_or_create_car_make(make, raise_on_existing=False)

    if isinstance(model, str):
        model = get_or_create_car_model(make, model, raise_on_existing=False)

    qs = Car.objects.filter(car_id__exact=car_id)
    if qs.count():
        if raise_on_existing:
            raise CarpoolAlreadyExistsError(car_id=car_id)

        car = qs.get()

        if registration_number != car.registration_number:
            raise CarpoolInconsistentError(
                'wrong registration number',
                expected=registration_number,
                found=car.registration_number,
            )

        if model != car.model:
            raise CarpoolInconsistentError('wrong model', expected=model, found=car.model)

        if make != car.model.make:
            raise CarpoolInconsistentError('wrong make', expected=make, found=car.model.make)

        return car

    return Car.objects.create(
        model=model,
        car_id=car_id,
        registration_number=registration_number,
    )


def all_cars(ascending_order: bool = True):
    """List all cars with configurable ordering direction. Always ordering by car_id."""

    prefix = ''
    if not ascending_order:
        prefix = '-'

    return Car.objects.order_by(f'{prefix}car_id').all()


def _get_car_by_car_id(car_id: str) -> Car:
    validate_car_id(car_id)

    try:
        return Car.objects.get(car_id=car_id)
    except Car.DoesNotExist:
        raise CarpoolNotFoundError(f'not found car with {car_id=}')


def delete_car(car_id: str) -> Car:
    """Delete single car selected based on car_id."""

    _log = log.bind(car_id=car_id)
    _log.info('requested car delete', ts=now())

    try:
        car = _get_car_by_car_id(car_id)
    except CarpoolNotFoundError:
        _log.error('not found car for deletion')
        raise

    car.delete()
    _log.info('successfully deleted car', ts=now())

    car.pk = None
    car.id = None
    return car


def update_car(
        car_id: str,
        registration_number: str | None = None,
        model: str | None = None,
        make: str | None = None,
) -> Car:
    """Update registration number and/or model_name and/or make of a single car selected by the given car ID."""

    attrs_to_update = [
        name
        for attr, name in ((registration_number, 'registration_number'), (model, 'model'), (make, 'make'))
        if attr is not None
    ]
    if not len(attrs_to_update):
        raise ValueError('missing at least one attribute to be updated')
    if (model and not make) or (not model and make):
        raise ValueError('make and model_name has to be updated together or none of them')

    car = _get_car_by_car_id(car_id)
    car.registration_number = registration_number
    if model:
        make = get_or_create_car_make(make, raise_on_existing=False)
        car.model = get_or_create_car_model(make, model, raise_on_existing=False)

        attrs_to_update.remove('make')  # update cannot be transitive
        car.model.make = make
        car.model.save(update_fields=['make', 'date_updated'])

    attrs_to_update.append(date_updated)
    car.save(update_fields=attrs_to_update)

    return _get_car_by_car_id(car_id)
