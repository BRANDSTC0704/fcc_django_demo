# myapp/subapp1/urls.py
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('kuebel_aktivitaet', views.kuebel_page, name='kuebel_aktivitaet'),
    path('print-pdf/<int:log_id>/', views.generate_pdf, name='generate_pdf'),
    path('open-pdf/<int:log_id>/', views.open_pdf_redirect, name='open_pdf_redirect'),
    path('admin', views.admin_view, name='admin'),
]