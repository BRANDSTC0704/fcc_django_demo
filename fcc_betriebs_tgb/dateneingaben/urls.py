# myapp/subapp1/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.kuebel_page, name='home'),  # Make sure this exists
    path('', views.kuebel_page, name='kuebel_aktivitaet'),
]