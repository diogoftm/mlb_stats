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
    def game_link(id):
        info = statsapi.get('game_contextMetrics', {'gamePk':id})['game']
        home_team = {'name': info['teams']['home']['team']['name'], 'record': "%s-%s".format(info['teams']['home']['team']['leagueRecord']['wins'], info['teams']['home']['team']['leagueRecord']['losses']), 'score': info['teams']['home']['score']}
        home_team = {'name': info['teams']['away']['team']['name'], 'record': "%s-%s".format(info['teams']['away']['team']['leagueRecord']['wins'], info['teams']['away']['team']['leagueRecord']['losses']), 'score': info['teams']['away']['score']}
        date = info['officialDate']
        venue = info['venue']['name']
        series = info['seriesDescription']
        status = info['status']['abstractGameState']

