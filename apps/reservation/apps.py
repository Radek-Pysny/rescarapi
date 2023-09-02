from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReservationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reservation'
    verbose_name = _('reservation')
