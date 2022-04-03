from django.shortcuts import render, redirect
import json


def home(request):
    with open('games_today.json', 'r') as js:
        j = json.load(js)['games']
        return render(request,'stats/index.html', {'title': 'Home', 'games': j})


def stats(request):
    return render(request,'stats/index.html')


def list_game(request, game_id=None):
    return redirect(f"https://www.mlb.com/gameday/{game_id}/final/wrap")
