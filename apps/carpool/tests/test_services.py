import pytest
from django.core.exceptions import ValidationError
from structlog.testing import capture_logs

from apps.carpool import services as api
from apps.carpool.errors import CarpoolAlreadyExistsError, CarpoolInconsistentError, CarpoolNotFoundError
from apps.carpool.models import CarMake, CarModel, Car
from libs.testing import found_log, any_logged_value


def test__get_or_create_car_make__empty_name():
    with pytest.raises(ValueError) as ex:
        api.get_or_create_car_make(name=None)
    assert str(ex.value) == "empty name"

    with pytest.raises(ValueError) as ex:
        api.get_or_create_car_make(name="")
    assert str(ex.value) == "empty name"


def test__get_or_create_car_make__new_object_only_name(db):
    assert CarMake.objects.count() == 0
    # official name taken from name
    name = 'VW'
    new_make = api.get_or_create_car_make(name=name)
    assert new_make is not None
    assert new_make.name == name
    assert new_make.official_name == name


def test__get_or_create_car_make__new_object_name_and_official_name(db):
    # explicitly stated official name
    name = 'Skoda'
    official_name = 'Skoda auto a.s.'
    new_make = api.get_or_create_car_make(name=name, official_name=official_name)
    assert new_make is not None
    assert new_make.name == name
    assert new_make.official_name == official_name


def test__get_or_create_car_make__new_objects_are_different(db):
    # each time different object
    names = ['Honda', 'Nissan']
    first_make = api.get_or_create_car_make(name=names[0])
    second_make = api.get_or_create_car_make(name=names[1])
    assert first_make.pk != second_make.pk
    assert first_make.name != second_make.name
    assert first_make.official_name != second_make.official_name


@pytest.fixture
def make_VW(db) -> CarMake:
    return CarMake.objects.create(
        name='VW',
        official_name='VW GmbH',
    )


def test__get_or_create_car_make__retrieve_existing_object(make_VW: CarMake):
    # retrieving already existing car make object
    old_make = api.get_or_create_car_make(name=make_VW.name)
    assert old_make is not None
    assert old_make.pk == make_VW.pk
    assert old_make.name == make_VW.name
    assert old_make.official_name == make_VW.official_name


def test__get_or_create_car_make__exception_on_existing_make(make_VW: CarMake):
    # retrieving already existing car make object
    with pytest.raises(CarpoolAlreadyExistsError) as ex:
        _ = api.get_or_create_car_make(name=make_VW.name, raise_on_existing=True)
    assert 'already exists' in str(ex.value)
    assert ex.value.type == 'make'
    assert ex.value.make_name == make_VW.name


def test__get_or_create_car_model__new_model_and_make(db):
    assert CarMake.objects.count() == 0
    assert CarModel.objects.count() == 0
    make_name = 'Tesla'
    model_name = '3'
    new_model = api.get_or_create_car_model(make=make_name, model_name=model_name)
    assert new_model is not None
    assert new_model.pk is not None
    assert new_model.name == model_name
    assert CarModel.objects.count() == 1
    new_make = new_model.make
    assert new_make is not None
    assert new_make.pk is not None
    assert new_make.name == make_name
    assert CarMake.objects.count() == 1


def test__get_or_create_car_model__new_model_but_existing_make(make_VW: CarMake):
    # reusing existing make but creating a new model_name
    assert CarModel.objects.count() == 0
    name = 'Passat'
    new_model = api.get_or_create_car_model(make=make_VW.name, model_name=name, raise_on_existing=False)
    assert new_model is not None
    assert new_model.name == name
    assert new_model.make.pk == make_VW.pk


@pytest.fixture
def model_VW_Golf(make_VW: CarMake) -> CarModel:
    return CarModel.objects.create(
        name='Golf',
        make=make_VW,
    )


def test__get_or_create_car_model__exception_on_existing_model(model_VW_Golf: CarModel):
    # retrieving already existing car model object
    with pytest.raises(CarpoolAlreadyExistsError) as ex:
        _ = api.get_or_create_car_model(make=model_VW_Golf.make, model_name=model_VW_Golf.name, raise_on_existing=True)
    assert 'already exists' in str(ex.value)
    assert ex.value.type == 'model'
    assert ex.value.model_name == model_VW_Golf.name


def test__get_or_create_car__new_car_model_and_make(db):
    assert Car.objects.count() == 0
    assert CarModel.objects.count() == 0
    assert CarMake.objects.count() == 0
    registration_number = 'CVK 3212'
    car_id = 'C25'
    make_name = 'Imperial'
    model_name = 'Tie Fighter'
    new_car = api.get_or_create_car(
        make=make_name,
        model=model_name,
        car_id=car_id,
        registration_number=registration_number,
    )
    assert new_car is not None
    assert new_car.pk is not None
    assert new_car.car_id == car_id
    assert new_car.registration_number == registration_number
    new_model = new_car.model
    assert new_model.pk is not None
    assert new_model.name == model_name
    new_make = new_model.make
    assert new_make.pk is not None
    assert new_make.name == make_name
    assert new_make.official_name == make_name
    assert Car.objects.count() == 1
    assert CarModel.objects.count() == 1
    assert CarMake.objects.count() == 1


def test__get_or_create_car__new_car_but_existing_make_and_model(model_VW_Golf: CarModel):
    assert Car.objects.count() == 0
    registration_number = '1SK 3667'
    car_id = 'C007'
    new_car = api.get_or_create_car(
        make=model_VW_Golf.make.name,
        model=model_VW_Golf.name,
        car_id=car_id,
        registration_number=registration_number,
    )
    assert new_car is not None
    assert new_car.pk is not None
    assert new_car.car_id == car_id
    assert new_car.registration_number == registration_number
    assert new_car.model.pk == model_VW_Golf.pk
    assert new_car.model.make.pk == model_VW_Golf.make.pk
    assert Car.objects.count() == 1


@pytest.fixture
def car_C1(model_VW_Golf: CarModel) -> Car:
    return Car.objects.create(
        car_id='C1',
        registration_number='NAC ELN1K',
        model=model_VW_Golf,
    )


@pytest.fixture
def car_C2(model_VW_Golf: CarModel) -> Car:
    return Car.objects.create(
        car_id='C2',
        registration_number='POB OCN1K',
        model=model_VW_Golf,
    )


def test__get_or_create_car__existing_car(car_C1: Car):
    old_car = api.get_or_create_car(
        make=car_C1.model.make.name.upper(),
        model=car_C1.model.name.upper(),
        car_id=car_C1.car_id,
        registration_number=car_C1.registration_number,
    )
    assert old_car is not None
    assert old_car.pk == car_C1.pk
    assert old_car.model.pk == car_C1.model.pk
    assert old_car.model.make.pk == car_C1.model.make.pk
    assert Car.objects.count() == 1
    assert CarModel.objects.count() == 1
    assert CarMake.objects.count() == 1


def test__get_or_create_car__exception_on_existing_car(car_C1: Car):
    # retrieving already existing car object
    with pytest.raises(CarpoolAlreadyExistsError) as ex:
        _ = api.get_or_create_car(
            make=car_C1.model.make.name,
            model=car_C1.model.name,
            car_id=car_C1.car_id,
            registration_number=car_C1.registration_number,
            raise_on_existing=True,
        )
    assert 'already exists' in str(ex.value)
    assert ex.value.type == 'car'
    assert ex.value.car_id == car_C1.car_id


def test__get_or_create_car__inconsistency_exception_registration_nr(car_C1: Car):
    different_registration_number = car_C1.registration_number.lower()
    with pytest.raises(CarpoolInconsistentError) as ex:
        _ = api.get_or_create_car(
            make=car_C1.model.make.name,
            model=car_C1.model.name,
            car_id=car_C1.car_id,
            registration_number=different_registration_number,
        )
    assert 'registration number' in str(ex.value)
    assert ex.value.expected == different_registration_number
    assert ex.value.found == car_C1.registration_number


def test__get_or_create_car__inconsistency_exception_model(car_C1: Car):
    different_model_name = car_C1.model.name + ' Super IV'
    with pytest.raises(CarpoolInconsistentError) as ex:
        _ = api.get_or_create_car(
            make=car_C1.model.make.name,
            model=different_model_name,
            car_id=car_C1.car_id,
            registration_number=car_C1.registration_number,
        )
    assert 'model' in str(ex.value)
    assert ex.value.expected.name == different_model_name
    assert ex.value.found == car_C1.model


def test__get_or_create_car__inconsistency_exception_make(car_C1: Car):
    different_make_name = 'another ' + car_C1.model.make.name
    with pytest.raises(CarpoolInconsistentError) as ex:
        _ = api.get_or_create_car(
            make=different_make_name,
            model=car_C1.model.name,
            car_id=car_C1.car_id,
            registration_number=car_C1.registration_number,
        )
    exception_message = str(ex.value)
    assert 'model' in exception_message or 'make' in exception_message


def test__all_cars__empty(db):
    cars = api.all_cars()
    assert len(cars) == 0


def test__all_cars__nonempty(car_C1: Car, car_C2: Car):
    cars = api.all_cars()
    assert len(cars) == 2
    assert [car.pk for car in cars] == [car_C1.pk, car_C2.pk]

    cars = api.all_cars(ascending_order=True)
    assert len(cars) == 2
    assert [car.pk for car in cars] == [car_C1.pk, car_C2.pk]

    cars = api.all_cars(ascending_order=False)
    assert len(cars) == 2
    assert [car.pk for car in cars] == [car_C2.pk, car_C1.pk]


def test___get_car_by_car_id__ok(car_C1: Car):
    car = api._get_car_by_car_id(car_C1.car_id)
    assert car is not None
    assert car.pk == car_C1.pk


def test___get_car_by_car_id__not_found_exception(car_C1: Car):
    different_car_id = car_C1.car_id + '0'
    with pytest.raises(CarpoolNotFoundError):
        _ = api._get_car_by_car_id(different_car_id)


def test__delete_car__ok(car_C1: Car):
    assert Car.objects.count() == 1
    assert CarModel.objects.count() == 1
    assert CarMake.objects.count() == 1
    ghost_car = api.delete_car(car_id=car_C1.car_id)
    assert ghost_car.pk is None
    assert ghost_car.id is None
    assert ghost_car.car_id == car_C1.car_id
    assert ghost_car.model == car_C1.model
    assert ghost_car.registration_number == car_C1.registration_number
    assert ghost_car.model.pk == car_C1.model.pk
    assert ghost_car.model.make.pk == car_C1.model.make.pk
    assert Car.objects.count() == 0
    assert CarModel.objects.count() == 1
    assert CarMake.objects.count() == 1


def test__delete_car__not_found_exception(car_C1: Car):
    different_car_id = car_C1.car_id + '0'
    assert Car.objects.count() == 1
    with pytest.raises(CarpoolNotFoundError):
        api.delete_car(car_id=different_car_id)
    assert Car.objects.count() == 1


def test__delete_car__car_id_validation_error():
    invalid_car_id = 'A-42'
    with pytest.raises(ValidationError):
        api.delete_car(car_id=invalid_car_id)


def test__delete_car__logging(car_C1: Car):
    different_car_id = car_C1.car_id + '0'
    with capture_logs() as logs:
        with pytest.raises(CarpoolNotFoundError):
            api.delete_car(car_id=different_car_id)
    assert len(logs) == 2
    assert found_log(
        logs,
        event='requested car delete',
        log_level='info',
        car_id=different_car_id,
        ts=any_logged_value,
    )
    assert found_log(
        logs,
        event='not found car for deletion',
        log_level="error",
        car_id=different_car_id,
    )

    car_id = car_C1.car_id
    with capture_logs() as logs:
        api.delete_car(car_id=car_id)
    assert len(logs) == 2
    assert found_log(
        logs,
        event='requested car delete',
        log_level='info',
        car_id=car_id,
        ts=any_logged_value,
    )
    assert found_log(
        logs,
        event='successfully deleted car',
        log_level='info',
        car_id=car_id,
        ts=any_logged_value,
    )


def test__update_car__complete__ok(car_C1):
    new_registration_number = car_C1.registration_number.lower()
    new_model_name = car_C1.model.name + ' Mk.II'
    new_make_name = car_C1.model.make.name + ' Mk.II'
    assert new_registration_number != car_C1.registration_number
    updated_car = api.update_car(
        car_id=car_C1.car_id,
        registration_number=new_registration_number,
        model=new_model_name,
        make=new_make_name,
    )
    assert updated_car.pk == car_C1.pk
    assert updated_car.car_id == car_C1.car_id
    assert updated_car.registration_number != car_C1.registration_number
    assert updated_car.registration_number == new_registration_number
    updated_model = updated_car.model
    assert updated_model.pk != car_C1.model.pk
    assert updated_model.name != car_C1.model.name
    assert updated_model.name == new_model_name
    updated_make = updated_model.make
    assert updated_make.pk != car_C1.model.make.pk
    assert updated_make.name != car_C1.model.make.name
    assert updated_make.name == new_make_name

    car_C1.refresh_from_db()
    assert updated_car.pk == car_C1.pk
    assert updated_car.car_id == car_C1.car_id
    assert updated_car.registration_number == car_C1.registration_number
    assert updated_car.model_id == car_C1.model_id


def test__update_car__partial__ok(car_C1):
    new_registration_number = car_C1.registration_number.lower()
    assert new_registration_number != car_C1.registration_number
    updated_car = api.update_car(car_id=car_C1.car_id, registration_number=new_registration_number)
    assert updated_car.pk == car_C1.pk
    assert updated_car.car_id == car_C1.car_id
    assert updated_car.registration_number != car_C1.registration_number
    assert updated_car.registration_number == new_registration_number
    assert updated_car.model_id == car_C1.model_id


def test__update_car__not_found_exception(car_C1: Car):
    different_car_id = car_C1.car_id + '0'
    with pytest.raises(CarpoolNotFoundError):
        api.update_car(car_id=different_car_id, registration_number='')


def test__update_car__no_attr_exception():
    any_car_id = 'C0'
    with pytest.raises(ValueError) as ex:
        api.update_car(car_id=any_car_id)
    assert str(ex.value) == 'missing at least one attribute to be updated'


def test__update_car__depending_attr_exception():
    any_car_id = 'C0'
    any_reg_nr = '1U2 3456'
    any_model = 'any model'
    any_make = 'any make'
    expected_error_message = 'make and model_name has to be updated together or none of them'

    with pytest.raises(ValueError) as ex:
        api.update_car(car_id=any_car_id, model=any_model)
    assert str(ex.value) == expected_error_message

    with pytest.raises(ValueError) as ex:
        api.update_car(car_id=any_car_id, make=any_make)
    assert str(ex.value) == expected_error_message

    with pytest.raises(ValueError) as ex:
        api.update_car(car_id=any_car_id, registration_number=any_reg_nr, model=any_model)
    assert str(ex.value) == expected_error_message

    with pytest.raises(ValueError) as ex:
        api.update_car(car_id=any_car_id, registration_number=any_reg_nr, make=any_make)
    assert str(ex.value) == expected_error_message


def test__update_car__car_id_validation_error():
    invalid_car_id = '3X'
    with pytest.raises(ValidationError):
        api.update_car(car_id=invalid_car_id, registration_number='')

    invalid_type_car_id = 3.12
    with pytest.raises(ValidationError):
        api.update_car(car_id=invalid_type_car_id, registration_number='')
