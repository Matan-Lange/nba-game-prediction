import os
import requests
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime
import time

load_dotenv("../.env")


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


def get_train_data():
    nba_api = NbaApi()

    seasons = ['2019','2020','2021']
    columns = ['id', 'season', 'date', 'arena', 'H_team', 'H_team_id', 'A_team', 'A_team_id', 'H_score', 'A_score', 'ref1',
               'ref2', 'ref3',
               'ties', 'leadChange', 'nugget']
    games = pd.DataFrame(columns=columns)

    for season in seasons:
        res = nba_api.get('games', {"season": season})
        obj = json.loads(res.text)
        json_formatted_str = json.dumps(obj, indent=4)

        for index, item in enumerate(obj['response']):
            try:
                id = item['id']
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

    date_s = datetime.now().date()
    path = f'raw_data/games/games{date_s}.csv'
    games.to_csv(path, index=False)


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

    path = f'raw_data/games_stats/games_stats{date_s}.csv'
    games_stats.to_csv(path, index=False)





