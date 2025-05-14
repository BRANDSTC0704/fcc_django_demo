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
from him2_kuebelwaschplatz import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from .views import logout_view

urlpatterns = [
    # path("", views.kuebel_page, name="Kuebelstation"),
    # path("", views.start_page, name="home"),
    path("him2_kuebelwaschplatz/", include("him2_kuebelwaschplatz.urls")),
    path("", views.start_page, name="start_page"),
    path("him2_dboard_kuebelwaschplatz/", include("him2_dboard_kuebelwaschplatz.urls")),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("him2_pressenlinie/", include("him2_pressenlinie.urls")),
]

# Serve static files (for Plotly)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
