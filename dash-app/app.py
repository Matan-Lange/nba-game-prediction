import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Input, Output
import datetime
import os


assets_path = os.getcwd() +'\\assets'
app = dash.Dash(__name__, assets_folder=assets_path,external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1'}])

header = dbc.Row([
    dbc.Col([
        html.H2('NBA Game Prediction', className='text-center',)
    ])
],id='header')

app.layout = dbc.Container([header], fluid=True)

if __name__ == '__main__':
    print(assets_path)
    print(__name__)
    app.run_server(debug=True)
