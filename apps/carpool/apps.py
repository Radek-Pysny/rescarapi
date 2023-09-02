from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CarpoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.carpool'
    verbose_name = _('car pool')
