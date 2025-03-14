from django.urls import path
from . import views

urlpatterns = [
    path('', views.entrance_page, name='entrance_page'),
    path('forms/', views.form_page, name='form_page'),
    path('views/', views.views_page, name='views_page'),
]