import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

#logo_link = 'https://www.nicepng.com/png/detail/163-1637042_vector-free-chewbacca-vector-head-chewbacca.png'
#logo_link = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBqOjxj2ccsPVGyMuVBgqRZCSzDn_Uh7E9OljlQzbpgdV8BlrRrbbxsENV7zZpj_QmULo&usqp=CAU'
logo_link = 'https://raw.githubusercontent.com/sjuanandres0/Chewbacca/master/img/Chewie.png'
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('ticker_data.csv', index_col='Date', parse_dates=True)
tickers = df.ticker.unique()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.Div(children=[
        html.H2("Hi Galaxy, I'm Chewie!", style={
            #'margin':'30px'
            'padding':'0px 20px 0px 20px'
            #,'border':'3px dotted lightblue'
            #,'background-color':'black'
            ,'color':'white'
            ,'display':'inline-block'
            #,'textAlign': 'center'
            }),
        html.Img(src=logo_link, style={
            'display':'inline-block' 
            ,'margin':'25px' 
            ,'height':'100px'
            #,'width':'100px'
            #,'border':'2px solid black'
            #,'textAlign': 'right'
            })
    ], style={'color':'black','background-color':'black'})
    ,dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider', 
                  'value': 'slider'}],
        value=['slider']
        #, style={'color':'white'}
        #, style={'display':'inline-block'}
    )
    ,dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in tickers],
        value='BTC-USD'
        #, style={'display':'inline-block'}
    )
    ,dcc.Graph(id="my_graph"
        #, style={'display':'inline-block'}
    ),
]
#    , style={'margin':'0 auto','background-color':'black'}
)

@app.callback(
    Output("my_graph", "figure"), 
    [Input("toggle-rangeslider", "value"),
    Input("dropdown","value")])

def display_candlestick(value_range_slider, ticker_dropdown):
    df_plot = df.copy(deep=True)
    df_plot = df_plot[df_plot['ticker']==ticker_dropdown]
    fig = go.Figure(go.Candlestick(
        x=df_plot.index,
        open=df_plot.Open,
        high=df_plot.High,
        low=df_plot.Low,
        close=df_plot.Close
    ))
    fig.update_layout(
        title = ticker_dropdown + ' historic OHLC'
        , xaxis_rangeslider_visible='slider' in value_range_slider
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)