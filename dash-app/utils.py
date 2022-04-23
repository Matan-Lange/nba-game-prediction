import pandas as pd
from data.get_data import NbaApi
import datetime as dt
from datetime import timedelta
import json

def get_weekly_games():
    """function returns dataframe of next coming week games"""
    today = dt.datetime.today()
    next_week = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0,7)]

    nba_api = NbaApi()

    df_games = pd.DataFrame(columns=['game_id','date','h_team_name','h_team_id','a_team_name','a_team_id'])

    for date in next_week:
        res = nba_api.get('games',{'date':date})
        obj = json.loads(res.text)
        for item in obj['response']:
            id = item['id']
            h_team_name = item['teams']['home']['name']
            h_team_id = item['teams']['home']['id']
            a_team_name = item['teams']['visitors']['name']
            a_team_id = item['teams']['visitors']['id']

        df_games.loc[len(df_games)] = [id,date,h_team_name,h_team_id,a_team_id,a_team_name]

    return df_games



