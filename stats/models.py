from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    team_id = models.IntegerField(null=True)
    name = models.TextField()
    short_name = models.CharField(max_length=20, default='')
    ac = models.CharField(max_length=5, default='')
    ballpark = models.TextField()

class Game(models.Model):
    game_id = models.IntegerField()
    season = models.IntegerField()
    home = models.ForeignKey(Team, related_name='home_team', on_delete=models.CASCADE, default=1)
    away = models.ForeignKey(Team, related_name='away_team', on_delete=models.CASCADE, default=1)
    score_home = models.IntegerField(default=0)
    score_away = models.IntegerField(default=0)
    home_sp = models.TextField(default='')
    away_sp = models.TextField(default='')
    innings = models.IntegerField(default=9)
    venue = models.TextField(default='')
    attendance = models.IntegerField(default=0)
    dayNight = models.CharField(max_length=1, default='d') 
    series_type = models.TextField(default='Regular Season')
    duration = models.IntegerField(default=0) 
    win = models.IntegerField(default=0)
    more_info = models.TextField(default='{}')
    ended = models.IntegerField(default=0)
    date = models.CharField(max_length=20, null=True)
    season = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Stats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    season = models.IntegerField()
    n_games = models.IntegerField()
    runs = models.IntegerField()
    runs_home_avg = models.FloatField()
    runs_away_avg = models.FloatField()
    attendance_max = models.IntegerField()
    attendance_min = models.IntegerField()
    attendance_avg = models.IntegerField()
    duration_min = models.IntegerField()
    duration_max = models.IntegerField()
    duration_avg = models.IntegerField()
    watched_teams_rank = models.TextField(default='')
    teams_wins_rank = models.TextField(default='')
    teams_losses_rank = models.TextField(default='')
    venue_rank = models.TextField(default='')
    sp_rank = models.TextField(default='')
    teams_stats = models.TextField(default='')
