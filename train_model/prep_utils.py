import pandas as pd
import numpy as np
import math
import time


# Home and road team win probabilities implied by Elo ratings and home court adjustment

def win_probs(home_elo, away_elo, home_court_advantage):
    h = math.pow(10, home_elo / 400)
    r = math.pow(10, away_elo / 400)
    a = math.pow(10, home_court_advantage / 400)

    denom = r + a * h
    home_prob = a * h / denom
    away_prob = r / denom

    return home_prob, away_prob


# odds the home team will win based on elo ratings and home court advantage

def home_odds_on(home_elo, away_elo, home_court_advantage):
    h = math.pow(10, home_elo / 400)
    r = math.pow(10, away_elo / 400)
    a = math.pow(10, home_court_advantage / 400)
    return a * h / r


# this function determines the constant used in the elo rating, based on margin of victory and difference in elo ratings
def elo_k(MOV, elo_diff):
    k = 20
    if MOV > 0:
        multiplier = (MOV + 3) ** (0.8) / (7.5 + 0.006 * (elo_diff))
    else:
        multiplier = (-MOV + 3) ** (0.8) / (7.5 + 0.006 * (-elo_diff))
    return k * multiplier


# updates the home and away teams elo ratings after a game

def update_elo(home_score, away_score, home_elo, away_elo, home_court_advantage):
    home_prob, away_prob = win_probs(home_elo, away_elo, home_court_advantage)

    if (home_score - away_score > 0):
        home_win = 1
        away_win = 0
    else:
        home_win = 0
        away_win = 1

    k = elo_k(home_score - away_score, home_elo - away_elo)

    updated_home_elo = home_elo + k * (home_win - home_prob)
    updated_away_elo = away_elo + k * (away_win - away_prob)

    return updated_home_elo, updated_away_elo


# takes into account prev season elo
def get_prev_elo(team, date, season, team_stats, elo_df):
    prev_game = team_stats[team_stats['date'] < date][
        (team_stats['H_team_id'] == team) | (team_stats['A_team_id'] == team)].sort_values(by='date').tail(1).iloc[0]

    if team == prev_game['H_team_id']:
        elo_rating = elo_df[elo_df['Game_ID'] == prev_game['game_id']]['H_Team_Elo_After'].values[0]
    else:
        elo_rating = elo_df[elo_df['Game_ID'] == prev_game['game_id']]['A_Team_Elo_After'].values[0]

    if prev_game['season'] != season:
        return (0.75 * elo_rating) + (0.25 * 1505)
    else:
        return elo_rating


def create_elo_rating(df):
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)

    elo_df = pd.DataFrame(columns=['Game_ID', 'H_Team', 'A_Team',
                                   'H_Team_Elo_Before', 'A_Team_Elo_Before', 'H_Team_Elo_After', 'A_Team_Elo_After'])
    teams_elo_df = pd.DataFrame(columns=['Game_ID', 'Team', 'Elo', 'Date', 'Where_Played', 'Season'])

    for index, row in df.iterrows():
        game_id = row['game_id']
        game_date = row['date']
        season = row['season']
        h_team, a_team = row['H_team_id'], row['A_team_id']
        h_score, a_score = row['H_score'], row['A_score']

        if (h_team not in elo_df['H_Team'].values and h_team not in elo_df['A_Team'].values):
            h_team_elo_before = 1500
        else:
            h_team_elo_before = get_prev_elo(h_team, game_date, season, df, elo_df)

        if (a_team not in elo_df['H_Team'].values and a_team not in elo_df['A_Team'].values):
            a_team_elo_before = 1500
        else:
            a_team_elo_before = get_prev_elo(a_team, game_date, season, df, elo_df)

        h_team_elo_after, a_team_elo_after = update_elo(h_score, a_score, h_team_elo_before, a_team_elo_before, 100)

        new_row = {'Game_ID': game_id, 'H_Team': h_team, 'A_Team': a_team, 'H_Team_Elo_Before': h_team_elo_before,
                   'A_Team_Elo_Before': a_team_elo_before, \
                   'H_Team_Elo_After': h_team_elo_after, 'A_Team_Elo_After': a_team_elo_after}
        teams_row_one = {'Game_ID': game_id, 'Team': h_team, 'Elo': h_team_elo_before, 'Date': game_date,
                         'Where_Played': 'Home', 'Season': season}
        teams_row_two = {'Game_ID': game_id, 'Team': a_team, 'Elo': a_team_elo_before, 'Date': game_date,
                         'Where_Played': 'Away', 'Season': season}

        elo_df = elo_df.append(new_row, ignore_index=True)
        teams_elo_df = teams_elo_df.append(teams_row_one, ignore_index=True)
        teams_elo_df = teams_elo_df.append(teams_row_two, ignore_index=True)

    elo_df.rename({'Game_ID': 'game_id'}, axis=1, inplace=True)
    return elo_df



# create target varible - home win = 1 , away win = 0

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
    else: return 0




def win_perc(games_stats):
    games_stats.sort_values(by = ['season','team_id','date'], ascending = True, inplace = True)
    team_stats_groupby = games_stats.groupby(['team_id'])

    games_stats['game_number'] = team_stats_groupby.cumcount()
    games_stats['wins_before'] = team_stats_groupby['game_true_result'].apply(lambda x : x.shift().cumsum())
    games_stats['w_per_before'] = games_stats['wins_before']/games_stats['game_number']

    games_stats['w_per_last10games'] = team_stats_groupby['game_true_result'] \
                        .rolling(10, closed='left').sum() \
                        .reset_index(drop=True, level=0)
    games_stats['w_per_last5games'] = team_stats_groupby['game_true_result'] \
                        .rolling(5, closed='left').sum() \
                        .reset_index(drop=True, level=0)

    # games_stats.loc[games_stats['game_number']==0, 'elo_before'] = 1500
    games_stats['elo_before'] = games_stats['game_number'].apply(lambda x : 1500 if x==0 else np.nan)
    return games_stats


def rolling_avg(games_stats, columns_to_aggregate):
    columns_aggregated = ['mean_' + col for col in columns_to_aggregate]

    team_stats_groupby = games_stats.groupby(['team_id'])
    games_stats[columns_aggregated] = \
        team_stats_groupby[columns_to_aggregate].rolling(10, closed='left').mean().reset_index(drop=True, level=0)

    return games_stats
