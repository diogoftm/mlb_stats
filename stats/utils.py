from .models import Stats
from . import stats

import threading
from django.contrib.auth.models import User
import json


def periodic_task(interval, times = -1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap

def update_teams():
    """
    ! Updates the stats_team table.
    """
    from .models import Team
    import statsapi
    teams = statsapi.get('teams',{'sportIds':1,'activeStatus':'Yes', 'fields':'teams,name,id,abbreviation,name,shortName,venue'})['teams']
    Team.objects.all().delete()
    for te in teams:
        Team(team_id=te['id'], name=te['name'], short_name=te['shortName'], ac=te['abbreviation'], ballpark=te['venue']['name']).save()

def create_user_stats(user : User, season : int):
    """
    ! Create/update user stats for a given season 
    """
    runs_avgs : list = stats.avg_runs_stats(user, season=season)
    attendance_stats : list = stats.attendance_stats(user, season=season)
    duration_stats : list = stats.time_duration_stats(user, season=season)
    if len(Stats.objects.filter(user=user, season=season))==0:
        Stats(user=user, season=season, n_games=stats.n_games_watched_stats(user, season=season),
            runs=stats.n_runs_stats(user, season=season), runs_home_avg=runs_avgs[0][1],
            runs_away_avg=runs_avgs[1][1], 
            attendance_max=attendance_stats[1][1],
            attendance_min=attendance_stats[2][1], attendance_avg=attendance_stats[0][1],
            duration_min=duration_stats[2][1], duration_max=duration_stats[1][1], 
            duration_avg=duration_stats[0][1], 
            watched_teams_rank=json.dumps(stats.most_watched_team_stats(user, season=season)),
            teams_wins_rank=json.dumps(stats.win_loss_stats(user, season=season)['wins']),
            teams_losses_rank=json.dumps(stats.win_loss_stats(user, season=season)['loses']),
            venue_rank=json.dumps(stats.most_frequent_venue_stats(user, season=season)),
            sp_rank=json.dumps(stats.most_watched_sp_stats(user, season=season)),
            teams_stats=json.dumps(stats.teams_stats(user, season=season))).save()
    else:
        Stats.objects.filter(user=user, season=season).update(
            n_games=stats.n_games_watched_stats(user, season=season),
            runs=stats.n_runs_stats(user, season=season), runs_home_avg=runs_avgs[0][1],
            runs_away_avg=runs_avgs[1][1], 
            attendance_max=attendance_stats[1][1],
            attendance_min=attendance_stats[2][1], attendance_avg=attendance_stats[0][1],
            duration_min=duration_stats[2][1], duration_max=duration_stats[1][1], 
            duration_avg=duration_stats[0][1], 
            watched_teams_rank=json.dumps(stats.most_watched_team_stats(user, season=season)),
            teams_wins_rank=json.dumps(stats.win_loss_stats(user, season=season)['wins']),
            teams_losses_rank=json.dumps(stats.win_loss_stats(user, season=season)['loses']),
            venue_rank=json.dumps(stats.most_frequent_venue_stats(user, season=season)),
            sp_rank=json.dumps(stats.most_watched_sp_stats(user, season=season)),
            teams_stats=json.dumps(stats.teams_stats(user, season=season))
        )
    
