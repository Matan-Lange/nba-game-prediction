import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Input, Output
from utils import get_weekly_games
from datetime import datetime
import pickle

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1'}])

date_s = datetime.now().date()
path = f'..\\train_model\\pickeld_models\\model{date_s}.sav'
model = pickle.load(open(path, 'rb'))
games_stats = pd.read_csv(f'../train_model/raw_data/games_stats/games_stats{date_s}.csv')
games = pd.read_csv(f'../train_model/raw_data/games/games{date_s}.csv')

header = dbc.Row([
    dbc.Col([
        html.H2('NBA Game Prediction', className='text-center', )
    ])
], id='header')

div1 = html.Div([], id='div1')

new_games = get_weekly_games()
table = dash_table.DataTable(new_games.to_dict('records'),
                             [{"name": 'Game Id', "id": 'game_id'}, {"name": 'Date', "id": 'date'},
                              {"name": 'Home Team', "id": 'h_team_name'},
                              {"name": 'Away Team', "id": 'a_team_name'}
                              ], row_selectable='single',
                             id='datatable-interactivity', style_table={'margin-top': '20px'})

app.layout = dbc.Container([header, table, div1], fluid=True)


@app.callback(
    Output('div1', "children"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(row):
    from utils import model_input

    if row != []:
        row_num = row[0]
        row_data = dict(new_games.iloc[row_num])
        h_team_id = row_data['h_team_id']
        a_team_id = row_data['a_team_id']
        model_input = model_input(h_team_id, a_team_id, games=games, games_stats=games_stats)
        y_pred = model.predict([model_input])
        print(y_pred)
        return '0'
    else:
        return 0


if __name__ == '__main__':
    app.run_server(debug=True)
