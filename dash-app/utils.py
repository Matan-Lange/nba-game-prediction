import pandas as pd
from train_model.get_data import NbaApi
import datetime as dt
from datetime import timedelta
import json


def get_weekly_games():
    """function returns dataframe of next coming week games"""
    today = dt.datetime.today()
    next_week = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 7)]

    nba_api = NbaApi()

    df_games = pd.DataFrame(columns=['game_id', 'date', 'h_team_name', 'h_team_id', 'a_team_id', 'a_team_name', ])

    for date in next_week:
        res = nba_api.get('games', {'date': date})
        obj = json.loads(res.text)
        for item in obj['response']:
            id = item['id']
            h_team_name = item['teams']['home']['name']
            h_team_id = item['teams']['home']['id']
            a_team_name = item['teams']['visitors']['name']
            a_team_id = item['teams']['visitors']['id']

        df_games.loc[len(df_games)] = [id, date, h_team_name, h_team_id, a_team_id, a_team_name]

    return df_games


# fix elo
def get_elo(home_team_id, away_team_id):
    date_s = dt.datetime.now().date()
    elo_df = pd.read_csv(f'../train_model/prep_data/elo{date_s}.csv')

    h_last_game = elo_df[(elo_df['H_Team'] == home_team_id) | (elo_df['A_Team'] == home_team_id)]['game_id'].max()

    if len(elo_df[(elo_df['game_id'] == h_last_game) & (elo_df['H_Team'] == home_team_id)]['H_Team_Elo_After']) == 1:
        h_team_elo = \
        elo_df[(elo_df['game_id'] == h_last_game) & (elo_df['H_Team'] == home_team_id)]['H_Team_Elo_After'].values[0]
    else:
        h_team_elo = \
        elo_df[(elo_df['game_id'] == h_last_game) & (elo_df['A_Team'] == home_team_id)]['A_Team_Elo_After'].values[0]

    a_last_game = elo_df[(elo_df['H_Team'] == away_team_id) | (elo_df['A_Team'] == away_team_id)]['game_id'].max()

    if len(elo_df[(elo_df['game_id'] == a_last_game) & (elo_df['H_Team'] == away_team_id)]['H_Team_Elo_After']) == 1:
        a_team_elo = \
        elo_df[(elo_df['game_id'] == a_last_game) & (elo_df['H_Team'] == away_team_id)]['H_Team_Elo_After'].values[0]
    else:
        a_team_elo = \
        elo_df[(elo_df['game_id'] == a_last_game) & (elo_df['A_Team'] == away_team_id)]['A_Team_Elo_After'].values[0]

    return h_team_elo, a_team_elo


def get_rolling_avg(home_team_id, away_team_id, games_stats):
    columns_to_aggregate = ['fastBreakPoints', 'pointsInPaint', 'biggestLead', 'secondChancePoints',
                            'pointsOffTurnovers',
                            'longestRun', 'points', 'fgm', 'fga', 'fgp', 'ftm', 'fta', 'ftp', 'tpm', 'tpa', 'tpp',
                            'offReb',
                            'defReb', 'totReb', 'assists', 'pFouls', 'steals', 'turnovers', 'blocks', 'plusMinus']

    home = games_stats[games_stats['team_id'] == home_team_id].sort_values('game_id', ascending=False)[0:10].copy()
    away = games_stats[games_stats['team_id'] == away_team_id].sort_values('game_id', ascending=False)[0:10].copy()

    home = home.groupby('team_id').mean().reset_index()
    away.groupby('team_id').mean().reset_index()

    home = home[columns_to_aggregate].copy()
    away = away[columns_to_aggregate].copy()

    home = list(home.iloc[0])
    away = list(away.iloc[0])

    return home, away


def game_result(h_score, a_score):
    if h_score > a_score:
        return 1
    else:
        return 0


def game_true_result(team_id, h_team_id, result):
    if team_id == h_team_id:
        return result
    elif result == 0:
        return 1
    else:
        return 0


def get_win_perc(home_team_id, away_team_id, games, games_stats):
    games.rename({'id': 'game_id'}, axis=1, inplace=True)
    games['result'] = games.apply(lambda x: game_result(x['H_score'], x['A_score']), axis=1)
    games_stats[['Home_team_id', 'game_h_team_result', 'Away_team_id']] = \
        games_stats.merge(games, on='game_id', how='left')[['H_team_id', 'result', 'A_team_id']]
    games_stats['game_true_result'] = games_stats.apply(
        lambda x: game_true_result(x['team_id'], x['Home_team_id'], x['game_h_team_result']), axis=1)

    home = games_stats[games_stats['team_id'] == home_team_id].sort_values('game_id')
    away = games_stats[games_stats['team_id'] == away_team_id].sort_values('game_id')

    A_w_per_before = away['game_true_result'].sum() / len(away)
    A_w_per_last10games = away['game_true_result'][0:10].sum() / 10
    A_w_per_last5games = away['game_true_result'][0:5].sum() / 15

    H_w_per_before = home['game_true_result'].sum() / len(away)
    H_w_per_last10games = home['game_true_result'][0:10].sum() / 10
    H_w_per_last5games = home['game_true_result'][0:5].sum() / 15

    return [H_w_per_before, H_w_per_last10games, H_w_per_last5games], [A_w_per_before, A_w_per_last10games,
                                                                       A_w_per_last5games]


def model_input(home_team_id, away_team_id, games, games_stats):
    elo_h, elo_a = get_elo(home_team_id, away_team_id)
    win_rate_h, win_rate_a = get_win_perc(home_team_id, away_team_id, games, games_stats)
    rolling_avg_h, rolling_avg_a = get_rolling_avg(home_team_id, away_team_id, games_stats)

    input = [elo_h, elo_a] + rolling_avg_h + win_rate_h + rolling_avg_a + win_rate_a
    return input
