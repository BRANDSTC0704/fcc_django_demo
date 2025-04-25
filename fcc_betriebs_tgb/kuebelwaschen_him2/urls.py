# myapp/subapp1/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.start_page, name="start_page"),
    path('kuebel_aktivitaet', views.kuebel_page, name='kuebel_aktivitaet'),
    # path('print-pdf/', views.generate_pdf, name='generate_pdf'), 
    path('print-pdf/<int:log_id>/', views.generate_pdf, name='generate_pdf'),
    path('open-pdf/<int:log_id>/', views.open_pdf_redirect, name='open_pdf_redirect'),
]