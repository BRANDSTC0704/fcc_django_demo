from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.entrance_page, name="entrance_page"),
    path("forms/", views.form_page, name="form_page"),
    path("views/", views.views_page, name="views_page"),
    # path("debug/", views.debug_view, name="debug_page"),  # Add debug page
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
