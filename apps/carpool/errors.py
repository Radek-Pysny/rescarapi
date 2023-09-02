class CarpoolError(ValueError):
    """Base exception/error type for carpool app."""


class CarpoolNotFoundError(CarpoolError):
    def __init__(self, *args):
        if len(args):
            super().__init__(*args)

        super().__init__('instance not found')


class CarpoolAlreadyExistsError(CarpoolError):
    """Exception to be raised when explicitly requested failure on already found object with main identifier."""

    def __init__(self, make_name: str = None, model_name: str = None, car_id: str = None):
        if sum([bool(x) for x in (make_name, model_name, car_id)]) != 1:
            raise AssertionError('expected exactly 1 argument')

        self.type = 'make' if make_name else 'model' if model_name else 'car'
        self.make_name = make_name
        self.model_name = model_name
        self.car_id = car_id
        super().__init__(f'{self.type} already exists')


class CarpoolInconsistentError(CarpoolError):
    """Exception meaning that values given during car retrieval has some inconsistency in depending attributes."""

    def __init__(self, message: str, expected, found):
        self.expected = expected
        self.found = found
        super().__init__(message)
