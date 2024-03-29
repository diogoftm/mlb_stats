from .models import Game, Team, Stats

from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q, Avg, Max, Min,Sum
from collections import Counter
import json


def basic_stats_bundle(user : User, season : int = None):
    user_season_stats = Stats.objects.filter(user=user, season=season)[0]
    return [{'title': "Nº games", 'type': "single", 'data': user_season_stats.n_games},
            {'title': "Runs", 'type': "single", 'data': user_season_stats.runs},
            {'title': "Runs average", 'type': "list", 'data': 
             [('combined', round(user_season_stats.runs_home_avg + user_season_stats.runs_away_avg,2)), ('home',user_season_stats.runs_home_avg), ('away', user_season_stats.runs_away_avg)]},
            {'title': "Attendance", 'type': "list", 'data': 
             [('avg',user_season_stats.attendance_avg), ('max',user_season_stats.attendance_max), ('min', user_season_stats.attendance_min)]},
            {'title': "Duration (minutes)", 'type': "list", 'data': 
             [('avg',user_season_stats.duration_avg), ('max',user_season_stats.duration_max), ('min', user_season_stats.duration_min)]},
            {'title': "Most watched teams", 'type': "rank", 'data': json.loads(user_season_stats.watched_teams_rank)},
            {'title': "Most watched sp", 'type': "rank", 'data': json.loads(user_season_stats.sp_rank)},
            {'title': "Most watched venue", 'type': "rank", 'data': json.loads(user_season_stats.venue_rank)},
            {'title': "Most wins", 'type': "rank", 'data': json.loads(user_season_stats.teams_wins_rank)},
            {'title': "Most loses", 'type': "rank", 'data': json.loads(user_season_stats.teams_losses_rank)}
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
    return [('home', round(q['score_home__avg'], 2)), ('away', round(q['score_away__avg'], 2))]

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
    if season: 
        q = Game.objects.filter(Q(user=user, ended=1, season=season)).aggregate(Avg('duration'), Max('duration'), Min('duration'))
    else:
        q = Game.objects.filter(Q(user=user, ended=1)).aggregate(Avg('duration'), Max('duration'), Min('duration'))
    return [('avg',int(q['duration__avg'])), ('max',q['duration__max']), ('min', q['duration__min'])]

def max_innings_duration_stats(user : User, season : int = None):
    if season:
        return Game.objects.filter(user=user, season=season).aggregate(Max('innings'))
    return Game.objects.filter(user=user).aggregate(Max('innings'))

def attendance_stats(user : User, season : int = None, team : Team = None):
    if season: q = Game.objects.filter(user=user, season=season, ended=1).aggregate(Avg('attendance'), Max('attendance'), Min('attendance'))
    else: q = Game.objects.filter(user=user, ended=1).aggregate(Avg('attendance'), Max('attendance'), Min('attendance'))
    return [('avg',int(q['attendance__avg'])), ('max',q['attendance__max']), ('min', q['attendance__min'])]

def dayNight_stats(user : User, season : int = None):
    if season: return {'day': Game.objects.filter(user=user,season=season,dayNight='day').count(), 
                    'night': Game.objects.filter(user=user,season=season,dayNight='night').count()}
    return {'day': Game.objects.filter(user=user,dayNight='day').count(), 
            'night': Game.objects.filter(user=user,dayNight='night').count()}

def win_loss_stats(user : User, season : int = None, depth : int = 3):
    if season: games = Game.objects.filter(user=user, season=season, ended=1).all()
    else: games = Game.objects.filter(user=user, ended=1).all()
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


def teams_stats(user : User, season : int = None):
    """
    returns batting, pitching and fielding stats for all teams
    """
    #return None
    if season: games = Game.objects.filter(user=user, season=season).all()
    else: games = Game.objects.filter(user=user).all()
    
    t_stats = {}

    for game in games:
        t = json.loads(game.more_info)['liveData']['boxscore']['teams']
        __update_team_stats(game.home.name, t['home']['teamStats'], t_stats)
        __update_team_stats(game.away.name, t['away']['teamStats'], t_stats)
    
    return t_stats

def stats_names():
    return {'n_watched': ['GW', 'Games Watched'], 'flyOuts': ['FO', 'Fly Outs'], 'groundOuts': ['GO', 'Ground Outs'],
            'runs': ['R', 'Runs'], 'doubles': ['D', 'Doubles '], 'triples':['T', 'Triples'], 
            'homeRuns':['HR', "Home Runs"], 'strikeOuts':['SO', 'Strike Outs'], 'baseOnBalls':['BB', 'Base on Balls'],
            'intentionalWalks': ['IW', 'Intentional Walks'], 'hits': ['H', 'Hits'], 'hitByPitch': ['HBP', 'Hit By Pitch'],
            'avg': ['AVG', 'Average'], 'atBats': ['AB', 'At Bats'], 'obp':['OBP', 'On Base Percentage'],
            'slg': ['SLG', 'Slugging Percentage'], 'ops': ['OPS', 'On Base % + Slugging %'], 'caughtStealing':['CS', 'Cought Stealing'],
            'stolenBases': ['SB', 'Stolen Bases'], 'stolenBasePercentage': ['SB%', 'Stolen Base Percentage'],
            'groundIntoDoublePlay': ['GIDP', 'Ground Into Double Play'], 'groundIntoTriplePlay': ['GITP', 'Ground Into Triple Play'],
            'plateAppearances': ['PA', 'Plate Appearances'], 'totalBases':['TB', 'Tatal Bases'], 'rbi':['RBI', 'Runs batted In'],
            'leftOnBase': ['LOB', 'Left On Base'], 'sacBunts':['SacB', 'Sacrafice Bunts'], 'sacFlies':['SF', 'Sacrafice Flies'],
            'catchersInterference':['CI', 'Catchers Interference'],
            'pickoffs': ['PO', 'Pick Offs'], 'atBatsPerHomeRun': ['ABHR', 'At Bats per Home Run'], 'singles': ['S', 'Singles'],
            'era': ['ERA', 'Earned Runs Average'], 'inningsPitched':['IP', 'Innings Pitched'],
            'savingOpportunities': ['SOP', 'Saving Opportunities'], 'numberOfPitches':['NP', 'NUmber Of Pitches'],
            'earnedRuns': ['ER', 'Earned Runs'], 'whip': ['WHIP', 'Walks Hits Per Inning Pitched'],
            'battersFaced': ['BF', 'Batters Faced'], 'completeGames': ['CG', 'Complete Games'],
            'errors': ['E', 'Errors'], 'chances': ['C', 'Chances']
            }

def __update_team_stats(team_name : str, team_stats : dict, t_stats : dict):
    if team_name not in t_stats:
        t_stats[team_name] = {'batting': team_stats['batting'], 'pitching': team_stats['pitching'], 
                              'fielding': team_stats['fielding']}
        t_stats[team_name]['batting']['singles'] = t_stats[team_name]['batting']['hits'] - t_stats[team_name]['batting']['doubles'] - t_stats[team_name]['batting']['triples'] - t_stats[team_name]['batting']['homeRuns']
        t_stats[team_name]['n_watched'] = 1
        t_stats[team_name]['pitching']['inningsPitched'] = float(t_stats[team_name]['pitching']['inningsPitched'])
    else:
        t_stats[team_name]['n_watched'] += 1
        for k in team_stats['batting']:
            if k == 'obp':
                t_stats[team_name]['batting'][k] = round((t_stats[team_name]['batting']['hits'] + t_stats[team_name]['batting']['baseOnBalls'] + t_stats[team_name]['batting']['hitByPitch']) / t_stats[team_name]['batting']['atBats'], 3)
            elif k == 'avg':
                t_stats[team_name]['batting'][k] = round(t_stats[team_name]['batting']['hits'] / t_stats[team_name]['batting']['atBats'], 3)
            elif k == 'ops':
                t_stats[team_name]['batting'][k] = round(t_stats[team_name]['batting']['slg'] + t_stats[team_name]['batting']['obp'],3)
            elif k == 'slg':
                t_stats[team_name]['batting'][k] = round((2*t_stats[team_name]['batting']['doubles'] + 3*t_stats[team_name]['batting']['triples'] + 4*t_stats[team_name]['batting']['homeRuns'] + t_stats[team_name]['batting']['singles']) / t_stats[team_name]['batting']['atBats'], 3)
            elif k == 'stolenBasePercentage':
                t_stats[team_name]['batting'][k] = round(t_stats[team_name]['batting']['stolenBases'] / (t_stats[team_name]['batting']['caughtStealing'] + t_stats[team_name]['batting']['stolenBases']), 3) if t_stats[team_name]['batting']['caughtStealing'] + t_stats[team_name]['batting']['stolenBases'] > 0 else '-'
            elif k == 'atBatsPerHomeRun':
                t_stats[team_name]['batting']['atBatsPerHomeRun'] = round(t_stats[team_name]['batting']['atBats'] / t_stats[team_name]['batting']['homeRuns'], 3) if t_stats[team_name]['batting']['homeRuns']>0 else '-'
            else:
                t_stats[team_name]['batting'][k] += team_stats['batting'][k]
        t_stats[team_name]['batting']['singles'] = t_stats[team_name]['batting']['hits'] - t_stats[team_name]['batting']['doubles'] - t_stats[team_name]['batting']['triples'] - t_stats[team_name]['batting']['homeRuns']


        for k in team_stats['pitching']:
            if k == 'obp':
                t_stats[team_name]['pitching'][k] = round((t_stats[team_name]['pitching']['hits'] + t_stats[team_name]['pitching']['baseOnBalls'] + t_stats[team_name]['pitching']['hitByPitch']) / t_stats[team_name]['batting']['atBats'], 3)
            elif k == 'stolenBasePercentage':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['stolenBases'] / (t_stats[team_name]['pitching']['caughtStealing'] + t_stats[team_name]['pitching']['stolenBases']), 3) if t_stats[team_name]['pitching']['caughtStealing'] + t_stats[team_name]['pitching']['stolenBases'] > 0 else '-'
            elif k == 'era':
                continue
            elif k == 'whip':
                t_stats[team_name]['pitching'][k] = round((t_stats[team_name]['pitching']['hits'] + t_stats[team_name]['pitching']['baseOnBalls'] ) / float(t_stats[team_name]['pitching']['inningsPitched']), 3)
            elif k == 'strikePercentage':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['strikes'] / t_stats[team_name]['pitching']['pitchesThrown'], 2)
            elif k == 'pitchesPerInning':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['pitchesThrown'] / t_stats[team_name]['pitching']['inningsPitched'], 1)
            elif k == 'runsScoredPer9':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['runs'] / t_stats[team_name]['pitching']['inningsPitched'] * 9, 1)
            elif k == 'homeRunsPer9':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['homeRuns'] / t_stats[team_name]['pitching']['inningsPitched'] * 9, 2)
            elif k == 'inningsPitched':
                t_stats[team_name]['pitching'][k] += float(team_stats['pitching'][k])
            elif k == 'groundOutsToAirouts':
                t_stats[team_name]['pitching'][k] = round(t_stats[team_name]['pitching']['groundOuts'] / t_stats[team_name]['pitching']['airOuts'], 2) if t_stats[team_name]['pitching']['airOuts'] > 0 else '-'
            else:
                t_stats[team_name]['pitching'][k] += team_stats['pitching'][k]
        
        t_stats[team_name]['pitching']['era'] = round(9*t_stats[team_name]['pitching']['earnedRuns'] / t_stats[team_name]['pitching']['inningsPitched'], 2) if t_stats[team_name]['pitching']['inningsPitched'] > 0 else '-'


        for k in team_stats['fielding']:
            if k == 'stolenBasePercentage':
                t_stats[team_name]['fielding'][k] = round(t_stats[team_name]['fielding']['stolenBases'] / (t_stats[team_name]['fielding']['stolenBases'] + t_stats[team_name]['fielding']['caughtStealing']), 2) if t_stats[team_name]['fielding']['stolenBases'] + t_stats[team_name]['fielding']['caughtStealing'] > 0 else '-'
            else:
                t_stats[team_name]['fielding'][k] += team_stats['fielding'][k]
