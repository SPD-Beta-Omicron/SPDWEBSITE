from django.apps import AppConfig


class SobersheetConfig(AppConfig):
    name = 'sobersheet'
    def ready(self):
        from . import signals  # noqa