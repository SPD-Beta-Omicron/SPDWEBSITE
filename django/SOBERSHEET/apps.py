from django.apps import AppConfig


class SobersheetConfig(AppConfig):
    name = 'SOBERSHEET'
    def ready(self):
        from . import signals  # noqa