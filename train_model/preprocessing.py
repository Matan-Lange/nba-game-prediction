import pandas as pd
from datetime import datetime
from prep_utils import *


def prep():
    date_s = datetime.now().date()
    print('run_prep')

    games = pd.read_csv(f'raw_data/games/games{date_s}.csv')
    games_stats = pd.read_csv(f'raw_data/games_stats/games_stats{date_s}.csv')
    games.rename({'id': 'game_id'}, axis=1, inplace=True)

    elo_df = create_elo_rating(games)
    elo_df.to_csv(f'prep_data/elo{date_s}.csv')
    games = games.merge(elo_df[['game_id', 'H_Team_Elo_Before', 'A_Team_Elo_Before']], on='game_id')

    # create target varible - home win = 1 , away win = 0
    games['result'] = games.apply(lambda x: game_result(x['H_score'], x['A_score']), axis=1)

    # join dates info to games_stats dataframe

    games_stats[['date', 'Home_team_id', 'game_h_team_result', 'Away_team_id']] = \
        games_stats.merge(games, on='game_id', how='left')[['date', 'H_team_id', 'result', 'A_team_id']]

    games_stats['game_true_result'] = games_stats.apply(
        lambda x: game_true_result(x['team_id'], x['Home_team_id'], x['game_h_team_result']), axis=1)
    games_stats['Opponent_team_id'] = games_stats.apply(
        lambda x: x['Away_team_id'] if x['Home_team_id'] == x['team_id'] else x['Home_team_id'], axis=1)
    games_stats.drop(['Home_team_id', 'game_h_team_result', 'Away_team_id'], axis=1, inplace=True)

    games_stats = games_stats.merge(games[['game_id', 'season']])

    games_stats = win_perc(games_stats)

    columns_to_aggregate = ['fastBreakPoints', 'pointsInPaint', 'biggestLead', 'secondChancePoints',
                            'pointsOffTurnovers',
                            'longestRun', 'points', 'fgm', 'fga', 'fgp', 'ftm', 'fta', 'ftp', 'tpm', 'tpa', 'tpp',
                            'offReb',
                            'defReb', 'totReb', 'assists', 'pFouls', 'steals', 'turnovers', 'blocks', 'plusMinus']

    games_stats = rolling_avg(games_stats, columns_to_aggregate)

    columns_aggregated = ['mean_' + col for col in columns_to_aggregate]

    relevant_columns = ['game_id', 'team_id'] + columns_aggregated + ['w_per_before', 'w_per_last10games',
                                                                      'w_per_last5games']
    # Home team data merge
    full_data = games.merge(right=games_stats[relevant_columns].add_prefix('H_'), left_on=['game_id', 'H_team_id'],
                            right_on=['H_game_id', 'H_team_id'])
    # Away team data merge
    full_data = full_data.merge(right=games_stats[relevant_columns].add_prefix('A_'), left_on=['game_id', 'A_team_id'],
                                right_on=['A_game_id', 'A_team_id'])

    drop = ['game_id', 'season', 'date', 'arena', 'H_team', 'H_team_id', 'A_team',
            'A_team_id', 'H_score', 'A_score', 'ref1', 'ref2', 'ref3', 'ties',
            'leadChange', 'nugget', 'H_game_id', 'A_game_id']

    full_data.drop(drop, axis=1, inplace=True)
    full_data.dropna(inplace=True)

    path = f'prep_data/model_data{date_s}.csv'
    full_data.to_csv(path, index=False)
