from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    game_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
