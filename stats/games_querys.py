import statsapi
import pytz
import json
from datetime import datetime
from .utils import periodic_task
from .models import Team


class Mlb:
    @staticmethod
    def games_at_date(date : str) -> list:
        """
        ! Returns some basic info from the games that started at a given date
        @param date : date formated as string like '%m/%d/%Y'
        @return list of games 
        """
        
        games = statsapi.schedule(date)
        g = []
        for i in games:
            g.append({'game_id': i['game_id'], 'home_team': Team.objects.filter(team_id=i["home_id"]).first().ac,
                      'home_score': i['home_score'], 'away_team': Team.objects.filter(team_id=i["away_id"]).first().ac,
                      'away_score': i['away_score'], 'time': pytz.timezone('UTC').localize(datetime.strptime(i['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone('Europe/London')).strftime("%H:%M"),
                      'inning': "{} {}".format(i['inning_state'], i['current_inning']), 'status': i['status']})
        return g

    @staticmethod
    @periodic_task(500)
    def refresh_added_games() -> None:
        from .models import Game
        """
        ! Refresh the status and some data of the unfinished games that here added.
        """
        games = Game.objects.get(ended=0)
        for g in games:
            i = Mlb.game_info(g.game_id)
            g.basic_info = json.dumps(i)
            g.ended = 1 if i['status']['statusCode']=='F' else 0
            g.score_home = i['teams']['home']['score']
            g.score_away = i['teams']['away']['score']
            g.save()

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
    

