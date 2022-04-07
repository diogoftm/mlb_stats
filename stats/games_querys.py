import statsapi
import pytz
import json
from datetime import datetime
from .utils import periodic_task


class Mlb:

    @staticmethod
    @periodic_task(300)
    def games_today_refresh():
        games = statsapi.schedule(start_date=datetime.today().strftime('%m/%d/%Y'))
        g = []
        x = 0
        for i in games:
            g.append({'game_id': i['game_id'], 'home_team': statsapi.lookup_team(i["home_id"])[0]["teamName"],
                      'home_score': i['home_score'], 'away_team': statsapi.lookup_team(i["away_id"])[0]["teamName"],
                      'away_score': i['away_score'], 'time': pytz.timezone('UTC').localize(datetime.strptime(i['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone('Europe/London')).strftime("%H:%M"),
                      'inning': "{} {}".format(i['inning_state'], i['current_inning']), 'status': i['status']})
            x += 1

        with open("games_today.json", "w+") as f:
            json.dump({"games": g}, f)
            f.close()

    @staticmethod
    def game_info(id):
        info = statsapi.get('game_contextMetrics', {'gamePk':id})['game']
        home_name = info['teams']['home']['team']['name']
        home_score = info['teams']['home']['score']
        away_name = info['teams']['away']['team']['name']
        away_score = info['teams']['away']['score']
        date = info['officialDate']
        return {'id': id ,'home':{'name': home_name, 'score': home_score}, 'away':{'name': away_name, 'score': away_score}, 'date': date}

    @staticmethod
    def game_has_ended(id):
        info = statsapi.get('game_contextMetrics', {'gamePk': id})['game']
        status = info['status']['abstractGameState']
        return status == 'Final'

