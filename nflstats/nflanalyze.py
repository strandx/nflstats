import nfldb, nfldbc, nflgame
import json

dbc = nfldbc.dbc

def get_team(team_name):
    with nfldb.Tx(dbc) as cursor:
        cursor.execute('SELECT * FROM team WHERE team_id = %s', [team_name,])
        return cursor.fetchone()

def get_all_teams():
    with nfldb.Tx(dbc) as cursor:
        cursor.execute('SELECT * FROM team;')
        return cursor.fetchall()

def get_stats_categories():
    return nfldb.stat_categories

def fuzzy_search(name):
    return nfldb.player_search(dbc, name, limit=30, team=None, position=None)

def get_player(last_name, first_name, team):
    with nfldb.Tx(dbc) as cursor:
        cursor.execute(
            '''SELECT * FROM player WHERE last_name = %s AND first_name = %s AND team = %s''',
            [last_name, first_name, team])
        player = cursor.fetchone()
        if player == None:
            team = 'UNK'
            cursor.execute(
                '''SELECT * FROM player WHERE last_name = %s AND first_name = %s AND team = %s''',
                [last_name, first_name, team])
            return cursor.fetchone()
        else:
            return player

def get_player_from_id(id):
    return nfldb.Player.from_id(dbc, id)

def get_player_all_time_stats(id):
    q = nfldb.Query(dbc)
    q.game(season_year=range(2009, 2016), season_type=['Regular', 'Postseason'])
    q.play_player(player_id=id)
    return q.limit(1).as_aggregate()

def get_player_stats_for_year(last_name, first_name, team, year):
    player = get_player(last_name, first_name, team)
    q = nfldb.Query(dbc)
    q.game(season_year=year, season_type=['Regular', 'Postseason'])
    q.play_player(player_id=player['player_id'])
    return q.limit(1).as_aggregate()

def get_player_all_time_stats_by_year(id):
    results = []
    for year in range(2009, 2016):
        q = nfldb.Query(dbc)
        q.game(season_year=year, season_type=['Regular', 'Postseason'])
        q.play_player(player_id=id)
        try:
            result = q.limit(1).as_aggregate()[0]
        except IndexError:
            continue
        else:
            result.year = year
            results.append(result)
    return results

def get_all_names():
    with nfldb.Tx(dbc) as cursor:
        cursor.execute(
            '''SELECT full_name, team, cast(position as varchar(20)), player_id FROM player''')
        names = cursor.fetchall()
        return names


def get_team_roster(team):
    q = nfldb.Query(dbc)
    players = q.player(team=team, status='Active').as_players()
    return players
