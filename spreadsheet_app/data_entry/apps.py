from django.apps import AppConfig


class DataEntryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_entry'

class DashAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dash_app"

    def ready(self):
        import data_entry.dash_apps  # 👈 Import dash_apps.py when Django starts