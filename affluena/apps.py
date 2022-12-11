from django.apps import AppConfig

class AffluenaConfig(AppConfig):
    name = 'Affluena'
    def ready(self):
        from affluena import signals