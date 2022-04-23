import os
import requests
from dotenv import load_dotenv
import json
import pandas as pd
import time

load_dotenv(".env")


class NbaApi:

    def __init__(self):
        self.url = "https://api-nba-v1.p.rapidapi.com/"
        self.credentials = {
            "X-RapidAPI-Host": os.environ.get(("HOST")),
            "X-RapidAPI-Key": os.environ.get(("API_KEY"))
        }

    def get(self, endpoint, params=None):
        if params is None:
            params = {}
        response = requests.request("GET", self.url + endpoint, headers=self.credentials, params=params)

        return response


nba_api = NbaApi()
res = nba_api.get('games', {"season": "2021"})
obj = json.loads(res.text)
json_formatted_str = json.dumps(obj, indent=4)

columns = ['id', 'season', 'date', 'arena', 'H_team', 'A_team_id', 'A_team', 'A_team_id', 'H_score', 'A_score', 'ref1',
           'ref2', 'ref3',
           'ties', 'leadChange', 'nugget']
games = pd.DataFrame(columns=columns)

for index, item in enumerate(obj['response']):
    try:
        id = item['id']
        season = '2021'
        date = item['date']['start']
        arena = item['arena']['name']
        h_team_name = item['teams']['home']['name']
        h_team_id = item['teams']['home']['id']
        a_team_name = item['teams']['visitors']['name']
        a_team_id = item['teams']['visitors']['id']
        h_score = item['scores']['home']['points']
        a_score = item['scores']['visitors']['points']
        ref1 = item['officials'][0]
        ref2 = item['officials'][1]
        ref3 = item['officials'][2]
        ties = item['timesTied']
        lead_change = item['leadChanges']
        nugget = item['nugget']

        row = [id, season, date, arena, h_team_name, h_team_id, a_team_name, a_team_id, h_score, a_score, ref1, ref2,
               ref3, ties, lead_change, nugget]

        games.loc[index] = row

    except Exception as e:
        print(e)

games.to_csv('data/games.csv', index=False)

#games = pd.read_csv('data//games.csv')
games_id = list(games['id'])
games_stats = pd.DataFrame()

for index, id in enumerate(games_id):
    try:
        nba_api = NbaApi()
        res = nba_api.get('games/statistics', {"id": id})
        obj = json.loads(res.text)

        if games_stats.empty:
            stats = obj['response'][0]['statistics']
            columns = stats[0].keys()

            columns = ['game_id', 'team_id'] + list(columns)
            games_stats = pd.DataFrame(columns=columns)

        data1 = [id, obj['response'][0]['team']['id']] + list(obj['response'][0]['statistics'][0].values())
        data2 = [id, obj['response'][1]['team']['id']] + list(obj['response'][1]['statistics'][0].values())

        games_stats.loc[len(games_stats)] = data1
        games_stats.loc[len(games_stats)] = data2

        print(index)

    except Exception as e:
        print(e)

games_stats.to_csv('data/games_stats.csv', index=False)


player_stats = pd.DataFrame()

for index, id in enumerate(games_id):
    try:
        nba_api = NbaApi()
        res = nba_api.get('players/statistics', {"game": id})
        obj = json.loads(res.text)

        if player_stats.empty:
            stats_exp = obj['response'][0]
            columns = stats_exp.keys()

            columns = ['player_name', 'team_id','game_id'] + list(columns)[3:]
            player_stats = pd.DataFrame(columns=columns)

        players_info = obj['response']

        for info in players_info:
            player_name = info['player']['firstname'] +' ' +info['player']['lastname']
            team_id = info['team']['id']
            game_id = id
            stats = info
            stats.pop('player')
            stats.pop('team')
            stats.pop('game')
            stats = [player_name,team_id,game_id] + list(stats.values())

            player_stats.loc[len(player_stats)] = stats

    except Exception as e:
        print(e)

player_stats.to_csv('data/player_stats.csv',index=False)
print('done')