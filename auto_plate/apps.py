from django.apps import AppConfig


class AutoPlateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auto_plate'
    verbose_name = "Автомобильные номера"
