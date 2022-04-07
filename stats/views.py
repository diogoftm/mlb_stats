from django.shortcuts import render, redirect
import json
from .models import Game
from .games_querys import Mlb


def home(request):
    with open('games_today.json', 'r') as js:
        j = json.load(js)['games']
        return render(request,'stats/index.html', {'title': 'Home', 'games': j})


def stats(request):
    games = Game.objects.filter(user_id=request.user.id)
    games_info = []
    for game in games:
        if Mlb.game_has_ended(game.game_id):
            games_info.append(Mlb.game_info(game.game_id))

    return render(request,'stats/stats.html', {'title': 'Stats', 'games_added': games_info})


def list_game(request, game_id=None):
    return redirect(f"https://www.mlb.com/gameday/{game_id}/final/wrap")
