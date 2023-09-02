import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


_re_car_id = re.compile(r'^C\d{1,10}$')


def validate_car_id(value):
    if not isinstance(value, str):
        raise ValidationError(_('invalid car id type') + f' ({type(value)})')

    if not _re_car_id.match(value):
        raise ValidationError(_('invalid car id') + f' ({value!s})')

