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
logo_link = 'https://raw.githubusercontent.com/sjuanandres0/Chewbacca/master/Chewie.png'
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('ticker_data.csv', index_col='Date', parse_dates=True)
tickers = df.ticker.unique()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.Div(children=[
        html.H2("Hi Galaxy, I'm Chewie!", style={
            #'margin':'30px'
            'padding':'30px'
            #,'border':'3px dotted lightblue'
            ,'background-color':'black'
            ,'color':'white'
            ,'display':'inline-block'
            #,'textAlign': 'center'
            }),
        html.Img(src=logo_link, style={
            'display':'inline-block' 
            #,'margin':'25px', 
            ,'height':'100px'
            ,'width':'100px'
            ,'border':'2px solid black'
            ,'textAlign': 'right'
            })
    ]),
#    dcc.Checklist(
#        id='toggle-rangeslider',
#        options=[{'label': 'Include Rangeslider', 
#                  'value': 'slider'}],
#        value=['slider']
#    ),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in tickers],
        value='BTC-USD'
    ),
    dcc.Graph(id="my_graph"),
])

@app.callback(
    Output("my_graph", "figure"), 
#    [Input("toggle-rangeslider", "value"),
#    Input("dropdown","value")])
    Input("dropdown","value"))

def display_candlestick(value):
    df_plot = df.copy(deep=True)#[df["ticker"]==lookup_ticker]
    df_plot = df_plot[df_plot['ticker']==value]
    fig = go.Figure(go.Candlestick(
        x=df_plot.index,#['Date'],
        open=df_plot.Open,#['AAPL.Open'],
        high=df_plot.High,#['AAPL.High'],
        low=df_plot.Low,#['AAPL.Low'],
        close=df_plot.Close#['AAPL.Close']
    ))
 #   fig.update_layout(
 #       xaxis_rangeslider_visible='slider' in value
 #   )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)