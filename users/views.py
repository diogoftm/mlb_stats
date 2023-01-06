from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import logout as django_logout
from .forms import UserRegisterForm
from stats.models import Game, Team
from stats.games_querys import Mlb
import json
import pytz
from datetime import datetime
import stats.stats as stats

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Bem vindo {username}! Já pode fazer o seu login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required()
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def logout(request, **kwargs):
    messages.success(request, 'Logged out.')
    django_logout(request)
    return redirect('stats-home')

@login_required
def add(request, game_id):
    g = Mlb.game_info(game_id, all=True)
    gci = Mlb.game_complete_info(game_id)
    ht = Team.objects.get(name=g['teams']['home']['team']['name'])
    at = Team.objects.get(name=g['teams']['away']['team']['name'])
    Game(game_id=game_id, user=request.user, basic_info=json.dumps(g), home=ht, away=at,
        score_home=g['teams']['home']['score'], score_away=g['teams']['away']['score'],
        win=0 if g['teams']['home']['isWinner'] else 1, ended=1 if g['status']['statusCode']=='F' else 0,
        home_sp=g['teams']['home']['probablePitcher']['fullName'], 
        away_sp=g['teams']['away']['probablePitcher']['fullName'], innings=g['scheduledInnings'], dayNight=g['dayNight'],
        series_type=g['seriesDescription'], venue=g['venue']['name'],
        attendance= gci['gameData']['gameInfo']['attendance'], duration=gci['gameData']['gameInfo']['gameDurationMinutes'],
        date=pytz.timezone('UTC').localize(datetime.strptime(g['gameDate'], '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone('Europe/London')).strftime("%m/%d/%YT%H:%M"), season=g['season'], ).save()
    messages.success(request, 'Jogo adicionado')
    return redirect('stats-home')

@login_required
def delete(request, game_id):
    game = Game.objects.filter(user=request.user, game_id=game_id).first()
    if game: 
        game.delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400) #game does not exist

@login_required
def list(request, season):
    """
    ! List games watched by a given user in a given season
    """
    if season == 0: 
        last_game = Game.objects.filter(user=request.user).last()
        if last_game: last_date = last_game.date
        else: 
            messages.error(request, f"You have no data yet")
            return redirect('stats-home')
        season = datetime.strptime(last_date, '%m/%d/%YT%H:%M').date().year
    q = Game.objects.filter(season = season, user_id = request.user).values('game_id','home__name', 'away__name', 'date', 'score_home', 'score_away')
    if not q:
        messages.error(request, f"{season} is a invalid season")
        return redirect('stats-home')

    if request.GET.get('load') == '1':
        data = render_to_string('stats/stats_base.html', {'season': season, 'games_list':q, 'stats': stats.basic_stats_bundle(request.user, season=season)})
        return JsonResponse({'data':data})
    return render(request, 'stats/load_stats.html', {'title': 'stats', 'season': season})

@login_required
def find(request, type):
    if type == "list":
        return redirect(f"/list/{request.GET.get('season')}")