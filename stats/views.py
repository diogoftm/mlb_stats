from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
import json
from .models import Game
from .games_querys import Mlb
from datetime import datetime


def home(request):
    games = Mlb.games_at_date(datetime.today().strftime('%m/%d/%Y'))
    if not games:
        return render(request, 'stats/index.html', {'title': 'Home', 
            'status': '<lottie-player src="https://assets1.lottiefiles.com/packages/lf20_19m6hu.json" background="transparent"  speed="0.5"  style="width: 300px; height: 300px;"  loop  autoplay></lottie-player> <h5 style="opacity: 0.5;">No games today</h5>'})
    return render(request, 'stats/index.html', {'games':games})
    

def games_at_date(request, date):
    date = date.replace('-','/')
    games = Mlb.games_at_date(date[-5:]+ '/' + date[:4])
    if not games:
        data = render_to_string('stats/games_base.html')
    else:
        data = render_to_string('stats/games_base.html', {'games': games})
    return JsonResponse({'data': data})

def list_game(request, game_id=None):
    return redirect(f"https://www.mlb.com/gameday/{game_id}/final/wrap")
