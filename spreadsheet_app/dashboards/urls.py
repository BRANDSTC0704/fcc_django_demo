from django.urls import path
from . import views
    
urlpatterns = [
    path("weekly/", views.weekly_dashboard, name="weekly_dashboard"),
    path("monthly/", views.monthly_dashboard, name="monthly_dashboard"),
]
