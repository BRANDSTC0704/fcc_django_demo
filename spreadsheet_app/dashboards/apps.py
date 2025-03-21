from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboards"

    def ready(self):
        import dashboards.dash_apps.weekly_dashboard
        import dashboards.dash_apps.monthly_dashboard

