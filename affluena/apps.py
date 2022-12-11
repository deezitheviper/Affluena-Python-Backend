from django.apps import AppConfig

class affluenaConfig(AppConfig):
    name = 'affluena'
    def ready(self):
        from affluena import signals