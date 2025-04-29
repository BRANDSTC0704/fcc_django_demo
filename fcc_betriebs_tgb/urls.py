"""
URL configuration for fcc_betriebs_tgb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from kuebelwaschen_him2 import views


urlpatterns = [
    # path("", views.kuebel_page, name="Kuebelstation"),
    # path("", views.start_page, name="home"),
    path("kuebelwaschen_him2/", include("kuebelwaschen_him2.urls")),
    path("", views.start_page, name="start_page"),
    path("dashboards/", include("dashboards.urls")),

    # path("admin/clearcache/", include("clearcache.urls")),
    # path("admin/", admin.site.urls),
    # path("", include("fcc_betriebs_tgb.urls")),
    # path("django_plotly_dash/", include("django_plotly_dash.urls")),
    # path("fcc_betriebs_tgb/", include("fcc_betriebs_tgb.urls")),
    # path("dashboards/", include("dashboards.urls")),
]

# Serve static files (for Plotly)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
