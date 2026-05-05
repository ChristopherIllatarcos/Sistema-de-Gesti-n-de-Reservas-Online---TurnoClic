from django.apps import AppConfig

class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas'

    def ready(self):
        # Comenta o elimina esta línea
        # import reservas.signals
        pass