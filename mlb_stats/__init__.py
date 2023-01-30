import django
django.setup()

from stats.games_querys import Mlb

Mlb.refresh_added_games()