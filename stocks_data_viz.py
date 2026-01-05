import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_ag_grid as dag
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialise app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initial data load
ticker_symbol = 'AAPL'
ticker = yf.Ticker(ticker_symbol)
price_data = ticker.history(period='1mo')
price_data = price_data.reset_index()

# App layout
app.layout = dbc.Container([
    # Title
    html.H1('Stock Price Dashboard', style={'textAlign': 'center', 'marginTop': 20}),
    
    # Last updated timestamp (will be updated via callback)
    html.Div(id='last_updated', style={'textAlign': 'center'}),
    
    # Dropdown for selecting y-axis
    dbc.Row([
        dbc.Col([
            html.Label('Select y-axis:'),
            dcc.Dropdown(
                id='y_column',
                options=[{'label': col, 'value': col} for col in ['Open', 'High', 'Low', 'Close']],
                value='Close'
            )
        ], width=6)
    ], style={'marginTop': 20}),
    
    # Graph
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='price_graph')
        ], width=12)
    ], style={'marginTop': 20}),
    
    # Data table
    dbc.Row([
        dbc.Col([
            dag.AgGrid(
                id='price_table',
                rowData=price_data.to_dict('records'),
                columnDefs=[{'field': i} for i in price_data.columns]
            )
        ], width=12)
    ], style={'marginTop': 20}),
    
    # Interval component for periodic updates
    dcc.Interval(
        id='interval_component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
])

# Callback for dropdown interaction and updating graph
@app.callback(
    Output('price_graph', 'figure'),
    Input('y_column', 'value')
)
def update_graph(selected_column):
    fig = px.line(price_data, x='Date', y=selected_column, 
                  title=f'{ticker_symbol} - {selected_column} Price')
    return fig

# Callback for periodic data update
@app.callback(
    [Output('price_table', 'rowData'),
     Output('last_updated', 'children')],
    Input('interval_component', 'n_intervals')
)
def update_data(n):
    # Fetch new data
    ticker = yf.Ticker(ticker_symbol)
    new_data = ticker.history(period='1mo')
    new_data = new_data.reset_index()
    
    # Timestamp for last update
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return new_data.to_dict('records'), f'Last updated: {timestamp}'

# Run app
if __name__ == '__main__':
    app.run(debug=True)
