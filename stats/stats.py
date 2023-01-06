from .models import Game, Team
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q, Avg, Max, Min, Case, When, F, Sum
from collections import Counter


def basic_stats_bundle(user : User, season : int = None):
    w_l = win_loss_stats(user, season=season)
    return [{'title': "Nº games", 'type': "single", 'data': n_games_watched_stats(user, season=season)},
            {'title': "Runs", 'type': "single", 'data': n_runs_stats(user, season=season)},
            {'title': "Runs average", 'type': "list", 'data': avg_runs_stats(user, season=season)},
            {'title': "Attendance", 'type': "list", 'data': attendance_stats(user, season=season)},
            {'title': "Duration (minutes)", 'type': "list", 'data': time_duration_stats(user, season=season)},
            {'title': "Most watched teams", 'type': "rank", 'data': most_watched_team_stats(user, season=season)},
            {'title': "Most watched sp", 'type': "rank", 'data': most_watched_sp_stats(user, season=season)},
            {'title': "Most watched venue", 'type': "rank", 'data': most_frequent_venue_stats(user, season=season)},
            {'title': "Most wins", 'type': "rank", 'data': w_l['wins']},
            {'title': "Most loses", 'type': "rank", 'data': w_l['loses']},
            ]

def most_watched_team_stats(user : User, season : int = None, depth : int = 3):
    if season:
        games = Game.objects.filter(user=user, season=season).values('home', 'away').annotate(n=Count('id'))
    else:
        games = Game.objects.filter(user=user).values('home', 'away').annotate(n=Count('id'))
    counter = Counter()
    for game in games:
        home_team = Team.objects.get(id=game['home'])
        away_team = Team.objects.get(id=game['away'])
        counter[home_team.name] += game['n']
        counter[away_team.name] += game['n']
    return sorted(counter.items(), key=lambda t1: -t1[1])[:depth]

def most_watched_sp_stats(user : User, season : int = None, depth : int = 3):
    if season:
        games = Game.objects.filter(user=user, season=season).values('home_sp', 'away_sp').annotate(n=Count('id'))
    else:
        games = Game.objects.filter(user=user).values('home_sp', 'away_sp').annotate(n=Count('id'))
    counter = Counter()
    for game in games:
        counter[game['home_sp']] += game['n']
        counter[game['away_sp']] += game['n']
    return sorted(counter.items(), key=lambda t1: -t1[1])[:depth]

def most_frequent_venue_stats(user : User, season : int = None, depth: int = 3):
    if season:
        return list(Game.objects.filter(user=user, season=season).values('venue').annotate(n=Count('venue')).order_by('-n').values_list('venue', 'n'))[:depth] 
    return Game.objects.filter(user=user).values('venue').annotate(n=Count('venue')).order_by('-n').values('venue', 'n').values_list('venue', 'n')[:depth]   

def n_games_watched_stats(user : User, season : int = None, team : Team = None):
    if season and team:
        return Game.objects.filter(Q(user=user) and Q(season=season) and (Q(home=team) or Q(away=team))).count()
    elif season:
        return Game.objects.filter(user=user, season=season).count()
    elif team:
        return Game.objects.filter(Q(user=user) and (Q(home=team) or Q(away=team))).count()
    else:
        return Game.objects.filter(user=user).count()

def avg_runs_stats(user : User, season : int = None, team : Team = None):
    """
    ! Avg runs stats
    """
    if (season and team) or team:
        if season: q = Game.objects.filter(Q(user=user) and Q(season=season) and (Q(home=team) or Q(away=team))).values('home', 'away','score_home', 'score_away')
        else: q = Game.objects.filter(Q(user=user) and (Q(home=team) or Q(away=team))).values('home', 'away','score_home', 'score_away')
        s_h, s_a, c_h, c_a = 0, 0, 0, 0
        for v in q:
            if v['home']==team.id: 
                s_h += v['score_home']
                c_h += 1
            else: 
                s_a += v['away']
                c_a += 1
        return {'avg': round((s_a+s_h)/(c_a+c_h), 2) if c_a!=0 or c_h!=0 else -1,
                'home': round(s_h/c_h, 2) if c_h!=0 else -1, 
                'away': round(s_a/c_a, 2) if c_a!=0 else -1}
    elif season:
        q = Game.objects.filter(user=user, season=season).aggregate(Avg('score_home'), Avg('score_away'))
    else:
        q = Game.objects.filter(user=user).aggregate(Avg('score_home'), Avg('score_away'))
    response = []
    response.append(('combined', round((q['score_home__avg'] + q['score_away__avg']), 2)))
    response.append(('home', round(q['score_home__avg'], 2)))
    response.append(('away', round(q['score_away__avg'], 2)))
    return response

def n_runs_stats(user : User, season : int = None):
    if season:
        total_runs = Game.objects.filter(user=user, season=season).aggregate(
            c=Sum('score_home') + Sum('score_away')
        )['c']
    else:
        total_runs = Game.objects.filter(user=user).aggregate(
            c=Sum('score_home') + Sum('score_away')
        )['c']
    return total_runs

def time_duration_stats(user : User, season : int = None) -> list:
    """
    return a dict with the average, min and max game duration
    """
    if season: q = Game.objects.filter(Q(user=user) and Q(season=season)).aggregate(Avg('duration'), Max('duration'), Min('duration'))
    q = Game.objects.filter(Q(user=user)).aggregate(Avg('duration'), Max('duration'), Min('duration'))
    return [('avg',int(q['duration__avg'])), ('max',q['duration__max']), ('min', q['duration__min'])]

def max_innings_duration_stats(user : User, season : int = None):
    if season:
        return Game.objects.filter(user=user, season=season).aggregate(Max('innings'))
    return Game.objects.filter(user=user).aggregate(Max('innings'))

def attendance_stats(user : User, season : int = None, team : Team = None):
    if season: q = Game.objects.filter(user=user, season=season).aggregate(Avg('attendance'), Max('attendance'), Min('attendance'))
    q = Game.objects.filter(user=user).aggregate(Avg('attendance'), Max('attendance'), Min('attendance'))
    return [('avg',int(q['attendance__avg'])), ('max',q['attendance__max']), ('min', q['attendance__min'])]

def dayNight_stats(user : User, season : int = None):
    if season: return {'day': Game.objects.filter(user=user,season=season,dayNight='day').count(), 
                    'night': Game.objects.filter(user=user,season=season,dayNight='night').count()}
    return {'day': Game.objects.filter(user=user,dayNight='day').count(), 
            'night': Game.objects.filter(user=user,dayNight='night').count()}

def win_loss_stats(user : User, season : int = None, depth : int = 3):
    games = Game.objects.filter(user=user, season=season, ended=1).all()
    q_w = {}
    q_l = {}
    for game in games:
        if game.score_home > game.score_away: 
            team_w = game.home.name
            team_l = game.away.name
        else: 
            team_w = game.away.name
            team_l = game.home.name

        if team_w not in q_w: q_w[team_w] = 1
        else: q_w[team_w] += 1
        if team_l not in q_l: q_l[team_l] = 1
        else: q_l[team_l] += 1

    return {'wins': sorted(q_w.items(), key=lambda t1: -t1[1])[:depth], 'loses': sorted(q_l.items(), key=lambda t1: -t1[1])[:depth]}

def day_of_week_stats(user : User, season : int = None):
    pass

def series_type_stats(user : User, season : int = None, team : Team = None):
    pass