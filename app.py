import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import chewie_pack
from dash.dash_table import DataTable, FormatTemplate

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
old_today = today - datetime.timedelta(days=120)

#logo_link = 'https://www.nicepng.com/png/detail/163-1637042_vector-free-chewbacca-vector-head-chewbacca.png'
#logo_link = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBqOjxj2ccsPVGyMuVBgqRZCSzDn_Uh7E9OljlQzbpgdV8BlrRrbbxsENV7zZpj_QmULo&usqp=CAU'
logo_link = 'https://raw.githubusercontent.com/sjuanandres0/Chewbacca/master/img/Chewie.png'
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('ticker_data.csv', index_col='Date', parse_dates=True)
df = df[df.index.year>=2010]
tickers = df.ticker.unique()

#d_columns = df.columns
money_format = FormatTemplate.money(2)
#d_columns = ['Date','Close'] + chewie_pack.indicators #,'sg_RSI_10','sg_RSI_50','sg_BB_10','sg_BB_50']
#d_columns = [{'name':x, 'id':x} for x in d_columns if x not in ['as','asd']]
d_columns = [
    dict(id='Date', name='Date'),
    dict(id='Close', name='Close', type='numeric', format=money_format),
] + [{'id':x, 'name':x} for x in chewie_pack.indicators]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.Div(children=[
        html.Img(src=logo_link, style={
            'display':'inline-block' 
            ,'margin':'0px'#'20px 10px 0px 10px' 
            ,'height':'40px'
            #,'width':'100px'
            #,'border':'1px solid white'
            ,'verticalAlign': 'top'
            #,'textAlign': 'right'
            })
        ,html.P("Hi Galaxy, I'm Chewie!", style={
            'margin':'0px'
            ,'padding':'0px 0px 0px 20px'
            #,'verticalAlign': 'top'
            ,'height':'40px'
            #,'border':'1px dotted lightblue'
            #,'background-color':'black'
            ,'color':'white'
            ,'display':'inline-block'
            #,'textAlign': 'center'
            #,'width': '100%', 
            #,'display': 'flex'
            ,'fontSize': '150%'
            #, 'align-items': 'center' 
            #,'justify-content': 'center'
            })
    ], style={'color':'black','background-color':'black','border':'0px dotted yellow'})
    ,html.Br()
    ,html.Div(children=[
        dcc.Dropdown(
            id='dropdown-ticker'
            ,options=[{'label': i, 'value': i} for i in tickers]
            ,value='BTC-USD'
            ,style={'background-color':'lightgrey'}
        )
        ,html.Br()
        ,dcc.DatePickerRange(id='date_picker'
            ,min_date_allowed = df.index.date.min()
            ,max_date_allowed = df.index.date.max()
            ,initial_visible_month = yesterday
            ,start_date = old_today
            ,end_date = yesterday
            ,style={'margin':'0 auto','background-color':'lightgrey'}
        )
        ,html.Br()
        ,html.Br()
        ,dcc.Checklist(
            id='toggle-rangeslider',
            options=[{'label': 'Include Rangeslider', 
                    'value': 'slider'}],
            value=['slider'], style={'color':'white'}
        )
    ], style={'display':'inline-block', 'verticalAlign': 'top', 'padding':'10px','width': '10%'})
    ,html.Div(children=[
#    ,html.Br()
        dcc.Graph(id="candle_graph"
        )
        ,dcc.Graph(id="pct_change_graph"
        )
        ,DataTable(
            id = 'datatable-signals',
            columns = d_columns,
            data = df.to_dict('records'),
            cell_selectable = False,
  			sort_action = 'native',
            #filter_action = 'native',
            page_action = 'native',
            page_current = 0,
            page_size = 10,
            style_header={'fontWeight':'bold', 'backgroundColor':'light-grey'},
            style_data = {'color':'white','backgroundColor':'black', 'border':'0px' },
            style_data_conditional=(
            [
                {
                    'if': {
                        'filter_query': '{{{col}}} = "sell"'.format(col=col),
                        'column_id': col
                    },
                    'color': 'tomato'
                } for col in chewie_pack.indicators
            ]+
            [
            {
                    'if': {
                        'filter_query': '{{{col}}} = "buy"'.format(col=col),
                        'column_id': col
                    },
                    'color': 'green'
                } for col in chewie_pack.indicators
            ]
            )
            )
    ], style={'display':'inline-block', 'padding':'10px','width': '85%'})
    #,html.Div(d_table, style={'width':'1000px', 'height':'350px', 'margin':'10px auto', 'padding-right':'30px'})
    ,html.P("Report updated: {}".format(today), style={
        'color':'white'
        #,'display':'inline-block'
        ,'text-align':'right'
    })
]
, style={'background-color':'black', 'padding':'10px', 'margin':'0px'}
)


@app.callback(
    Output("candle_graph", "figure"), 
    Output("pct_change_graph", "figure"),
    [Input("toggle-rangeslider", "value"),
    Input("dropdown-ticker", "value"),
    Input("date_picker", 'start_date'),
    Input("date_picker", 'end_date')
    ])

def display_candlestick(value_range_slider, ticker_dropdown, date_1, date_2):
    df_plot = df.copy(deep=True)
    #if end_date == None:
    #    end_date = old_today
    #df_plot = df.loc[np.logical_and((df.index.date > date_1), (df.index.date < date_2))]
    df_plot = df.loc[date_1:date_2]
    df_plot = df_plot[df_plot['ticker']==ticker_dropdown]
    
    fig_candle = go.Figure(go.Candlestick(
        x = df_plot.index,
        open = df_plot.Open,
        high = df_plot.High,
        low = df_plot.Low,
        close = df_plot.Close
    ))
    fig_candle.update_layout(
        title = ticker_dropdown + ' historic OHLC'
        ,xaxis_rangeslider_visible='slider' in value_range_slider
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font = {'color':'orange'}
        ,xaxis = {'showgrid':False}
    )

    fig_pct_change = px.line(df_plot, y='pct_change')
    fig_pct_change.update_layout(
        title = ticker_dropdown + ' historic Pct Change'
        ,xaxis_rangeslider_visible ='slider' in value_range_slider
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font={'color':'orange'}
        ,xaxis={'showgrid':False}
        )
    return fig_candle, fig_pct_change

@app.callback(
    Output('datatable-signals', 'data'),
    Input("dropdown-ticker", "value"))
def update_table(ticker_dropdown):
    df_copy = df.copy(deep=True)
    df_copy = df_copy[df_copy['ticker']==ticker_dropdown].sort_index(ascending=False).reset_index()[['Date','Close'] + chewie_pack.indicators]
    #df_copy['Date'] = datetime.date(df_copy['Date'])
    return df_copy.to_dict('records')
    #dff = df


if __name__ == '__main__':
    app.run_server(debug=True)