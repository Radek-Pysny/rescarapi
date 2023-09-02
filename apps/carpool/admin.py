from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CarMake, CarModel, Car


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    model = CarMake

    list_display = (
        'id', 'name', 'official_name',
    )


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    model = CarModel

    list_display = (
        'id', 'make', 'name',
    )


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    model = Car

    list_display = (
        'id', 'car_id', 'model', 'registration_number',
    )

    @admin.display(description=_('car make'))
    def get_make(self, obj: Car):
        return f'{obj.model.make}'
