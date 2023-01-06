import threading


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
