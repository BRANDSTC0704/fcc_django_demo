from django.apps import AppConfig


class DataEntryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_entry"


class DashAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dash_app"

    def ready(self):
        import dashboards.dash_apps.weekly_dashboard
        import dashboards.dash_apps.monthly_dashboard
