from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='stats-home'),
    path('stats/', views.stats, name='stats-stats'),
]