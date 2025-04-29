from django.urls import path
from . import views
    
urlpatterns = [
    path("grouped_dashboard/", views.grouped_dashboard, name="grouped_dashboard"),
]
