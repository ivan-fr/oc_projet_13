from django.apps import AppConfig


class VentesConfig(AppConfig):
    name = 'ventes'

    def ready(self):
        import ventes.signals
