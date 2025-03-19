from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/clearcache/", include("clearcache.urls")),
    path("admin/", admin.site.urls),
    path("", include("data_entry.urls")),
    path("django_plotly_dash/", include("django_plotly_dash.urls")),
    path("data_entry/", include("data_entry.urls")),
    path("dashboards/", include("dashboards.urls")),

]


# Serve static files (for Plotly)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
