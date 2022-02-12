from operator import index
import dash
import dash_bootstrap_components as dbc
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
import warnings
warnings.filterwarnings('ignore')

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
old_today = today - datetime.timedelta(days=120)

#logo_link = 'https://www.nicepng.com/png/detail/163-1637042_vector-free-chewbacca-vector-head-chewbacca.png'
#logo_link = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBqOjxj2ccsPVGyMuVBgqRZCSzDn_Uh7E9OljlQzbpgdV8BlrRrbbxsENV7zZpj_QmULo&usqp=CAU'
logo_link = 'https://raw.githubusercontent.com/sjuanandres0/Chewbacca/master/assets/Chewie.png'
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('ticker_data.csv', index_col='Date', parse_dates=True)
df = df[df.index.year>=2010]
tickers = df.ticker.unique()

money_format = FormatTemplate.money(2)
d_columns_signals = [
    dict(id='Date', name='Date'),
    dict(id='Close', name='Close', type='numeric', format=money_format),
] + [{'id':x, 'name':x} for x in chewie_pack.indicators]

d_columns_stats = ['Stat']+chewie_pack.strategies
d_columns_stats_dict = [{'id':x, 'name':x} for x in d_columns_stats]
df_stats = pd.DataFrame(columns=d_columns_stats, index=chewie_pack.stats_to_display)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Chewbacca'
#app = dash.Dash(__name__)
server = app.server

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "black",
}


app.layout = html.Div(children=[
    html.Div(children=[
        dbc.Nav(children=[
            html.Img(src=logo_link, style={
                'margin':'0px'#'20px 10px 0px 10px' 
                ,'height':'80px'
                ,'padding':'10px 0px 10px 30px'
                #,'text-align': 'center'
                })
            ,html.P(["Hi Galaxy, I'm Chewie!"], style={
                'margin':'0px'
                ,'padding':'2px'#'0px 0px 0px 20px'
                ,'height':'40px'
                ,'color':'white'
                ,'fontSize': '100%'
                ,'text-align': 'center'
                })
            ,html.Br()
            ,html.Br()
            ,dcc.Dropdown(
                id='dropdown_ticker'
                ,options=[{'label': i, 'value': i} for i in tickers]
                ,value='BTC-USD'
                ,style={'margin':'0px'}
            )
            ,html.Br()
            ,dcc.DatePickerRange(id='date_picker'
                ,min_date_allowed = df.index.date.min()
                ,max_date_allowed = df.index.date.max()
                ,initial_visible_month = yesterday
                ,start_date = old_today
                ,end_date = yesterday
                #,style={'margin':'10px'}
                #,style={'margin':'0 auto','background-color':'lightgrey'}
            )
            ,html.Br()
            ,html.Br()
            ,dcc.Checklist(
                id='rangeslider_toggle',
                options=[{'label': 'Include Rangeslider', 
                        'value': 'slider'}],
                value=['slider'], style={'color':'white'}
            )
            ,html.Br()
            ,html.P(["Report updated:", html.Br(), today], style={
                'color':'grey'
                ,'text-align':'bottom'
    })
        ], style=SIDEBAR_STYLE)#{'color':'black','background-color':'black','border':'0px dotted yellow'})
    ])
    ,html.Div(children=[
        dcc.Graph(id='graph_strategy')
        ,html.Br()
        ,DataTable(
            id = 'datatable_signals',
            columns = d_columns_signals,
            data = df.to_dict('records'),
            cell_selectable = False,
            sort_action = 'native',
            page_action = 'native',
            page_current = 0,
            page_size = 15,
            style_header={'fontWeight':'bold', 'backgroundColor':'light-grey'},
            style_data = {'color':'grey','backgroundColor':'black', 'border':'0px' },
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
        ,html.Br()
        ,DataTable(
            id = 'datatable_strategies_stats',
            columns = d_columns_stats_dict,
            data = df_stats.to_dict('records'),
            cell_selectable = False,
            sort_action = 'native',
            #filter_action = 'native',
            page_action = 'native',
            page_current = 0,
            page_size = 24,
            style_header={'fontWeight':'bold', 'backgroundColor':'light-grey'},
            style_data = {'color':'white','backgroundColor':'black', 'border':'0.2px solid grey' }
        )
        ,html.Br()
        ,dcc.Graph(id="graph_pct_change")
        ,html.Br()
        ,dcc.Graph(id="graph_candle")
    ], style={'background-color':'black', 'padding':'0px','margin':'0px 0px 0px 18rem'}) #style={'display':'inline-block', 'padding':'10px','width': '85%'})
], style={'background-color':'black', 'padding':'0px','margin':'0px'})


# CALLBACKs section

@app.callback(
    Output('graph_candle', 'figure'), 
    Output('graph_pct_change', 'figure'),
    [Input('rangeslider_toggle', 'value'),
    Input('dropdown_ticker', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date')
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
        title = '<b>{}</b> historic OHLC'.format(ticker_dropdown)
#        ,xaxis_rangeslider_visible='slider' in value_range_slider
        ,xaxis_rangeslider_visible=False
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font = {'color':'orange'}
        ,xaxis = {'showgrid':False,'title':None}
        ,yaxis={'showgrid':True,'gridcolor':'darkgrey'}
    )

    fig_pct_change = px.line(df_plot, y='pct_change')
    fig_pct_change.update_layout(
        title = '<b>{}</b> historic Pct Change'.format(ticker_dropdown)
#        ,xaxis_rangeslider_visible ='slider' in value_range_slider
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font={'color':'orange'}
        ,xaxis={'showgrid':False,'title':None}
        ,yaxis={'showgrid':True,'gridcolor':'darkgrey','title':None}
        )
    return fig_candle, fig_pct_change


@app.callback(
    Output('datatable_signals', 'data'),
    Input('dropdown_ticker', 'value'))
def update_table(ticker_dropdown):
    df_copy = df.copy(deep=True)
    df_copy = df_copy[df_copy['ticker']==ticker_dropdown].sort_index(ascending=False).reset_index()[['Date','Close'] + chewie_pack.indicators]
    #df_copy['Date'] = datetime.date(df_copy['Date'])
    return df_copy.to_dict('records')
    

@app.callback(
    Output('graph_strategy','figure'),
    Output('datatable_strategies_stats', 'data'),
    [Input('dropdown_ticker', 'value'),
    Input("date_picker", 'start_date'),
    Input("date_picker", 'end_date')
    ])
def update_strategy(ticker, start, end):
    bt_results = chewie_pack.strategies_eval(df, ticker, start, end)
    fig_strategies = px.line(bt_results.prices)
    fig_strategies.update_layout(
        title = '<b>{}</b> Backtesting Strategies'.format(ticker)
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font={'color':'orange'}
        ,xaxis={'showgrid':False,'gridcolor':'red','title':None}
        ,yaxis={'showgrid':True,'gridcolor':'darkgrey','title':None}
        ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.07,#1.02,
            xanchor="right",
            x=1
            ,font={'color':'white'}
            ,title=''
        ))
    table_stats = bt_results.stats.loc[chewie_pack.stats_to_display].astype(float).round(2).reset_index().rename(columns={'index':'Stat'})
    return fig_strategies, table_stats.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)