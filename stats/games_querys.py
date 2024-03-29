import statsapi
import pytz
import json
from datetime import datetime
from .utils import periodic_task
from .models import Team, Game
from .utils import create_user_stats

class Mlb:
    @staticmethod
    def games_at_date(date : str) -> list:
        """
        ! Returns some basic info from the games that started at a given date
        @param date : date formated as string like '%m/%d/%Y'
        @return list of games 
        """
        print(date)
        games = statsapi.schedule(date)
        g = []
        for i in games:
            try:
                g.append({'game_id': i['game_id'], 'home_team': Team.objects.filter(team_id=i["home_id"]).first().ac,
                        'home_score': i['home_score'], 'away_team': Team.objects.filter(team_id=i["away_id"]).first().ac,
                        'away_score': i['away_score'], 'time': pytz.timezone('UTC').localize(datetime.strptime(i['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone('Europe/London')).strftime("%H:%M"),
                        'inning': "{} {}".format(i['inning_state'], i['current_inning']), 'status': i['status']})
            except AttributeError: # if team for some reason is not from mlb
                continue
        return g

    @staticmethod
    @periodic_task(10)
    def refresh_added_games() -> None:
        """
        ! Refresh the status and some data about the unfinished games that here added.
        """
        games = Game.objects.filter(ended=0)
        for g in games:
            i = Mlb.game_info(g.game_id, all=True)
            gci = Mlb.game_complete_info(g.game_id)
            g.more_info = json.dumps(gci)
            g.ended = 1 if i['status']['statusCode']=='F' else 0
            g.score_home = i['teams']['home']['score']
            g.score_away = i['teams']['away']['score']
            if i['status']['statusCode']=='F':
                g.attendance = gci['gameData']['gameInfo']['attendance']
                g.duration = gci['gameData']['gameInfo']['gameDurationMinutes']
                g.win = 0 if i['teams']['home']['isWinner'] else 1
                g.basic_info = json.dumps(i)
            g.save()
            create_user_stats(g.user, g.season)
        

    @staticmethod
    def game_info(id : int, all : bool = False) -> dict:
        info = statsapi.get('game_contextMetrics', {'gamePk':id})['game']
        if all: return info
        home_name = info['teams']['home']['team']['name']
        home_score = info['teams']['home']['score']
        away_name = info['teams']['away']['team']['name']
        away_score = info['teams']['away']['score']
        date = info['officialDate']
        return {'id': id ,'home':{'name': home_name, 'score': home_score}, 'away':{'name': away_name, 'score': away_score}, 'date': date}

    @staticmethod
    def game_complete_info(id : int) -> dict:
        return statsapi.get('game', {'gamePk': id})

    @staticmethod
    def game_has_ended(id) -> bool:
        info = statsapi.get('game_contextMetrics', {'gamePk': id})['game']
        status = info['status']['abstractGameState']
        return status == 'Final'
    

