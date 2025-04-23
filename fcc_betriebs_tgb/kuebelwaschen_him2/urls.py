# myapp/subapp1/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.start_page, name="start_page"),
    # path('', views.kuebel_page, name='home'),  # Make sure this exists
    path('kuebel_aktivitaet', views.kuebel_page, name='kuebel_aktivitaet'),
]