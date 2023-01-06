from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='stats-home'),
    path('game/<int:game_id>', views.list_game, name='stats-game'),
    path('gamesAtDate/<str:date>', views.games_at_date ,name='find'),
]