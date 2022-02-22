from operator import index
import pandas as pd
import numpy as np
import datetime
import chewie_pack

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly
import plotly.graph_objects as go
import plotly.express as px
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

# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.title = 'Chewbacca'
#app = dash.Dash(__name__)
server = app.server

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    #"right": 0,
    "bottom": 0,
    "width": "14rem",
    "padding": "2rem 1rem",
    "background-color": "black",
    'z-index': '9999999'
}


app.layout = html.Div(children=[
    html.Div(children=[
        dbc.Nav(children=[
            html.Img(src=logo_link, style={
                'margin':'0px'#'20px 10px 0px 10px' 
                ,'height':'80px'
                #,"width": "100%"
                ,'padding':'10px 0px 10px 30px'
                #,'text-align': 'center'
                })
            #,html.P(["Hi Galaxy, I'm Chewie!"], style={
            ,html.P(["Hi Galaxy,", html.Br(), "I'm Chewie"], style={
                'margin':'0px'
                ,'padding':'2px'#'0px 0px 0px 20px'
                ,'height':'40px'
                ,'color':'white'
                ,'fontSize': '110%'
                ,'fontWeight':'bold'
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
            ,html.Br() ,html.Br()
            #,dcc.Checklist(id='rangeslider_toggle', options=[{'label':'Include Rangeslider', 'value':'slider'}], value=['slider'], style={'color':'white'})
            #,html.Br()
            
            ,html.Button("Download CSV", id="btn_csv", style={"width": "100%",'padding':0})
            ,dcc.Download(id="download-dataframe-csv")            
            ,html.Br() ,html.Br()
            ,html.Button("Download Excel", id="btn_xlsx", style={"width": "100%",'padding':0})
            ,dcc.Download(id="download-dataframe-xlsx")            
            
            ,html.Br() ,html.Br()
            ,html.A(
                children=[html.Img(src='https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png', style={"width": "100%",'padding':0})]
                ,href='https://www.buymeacoffee.com/s0juan', target="_blank"
            ) 

            ,html.A(
                children=[html.Img(src='https://raw.githubusercontent.com/sjuanandres0/Chewbacca/master/assets/GitHub-Mark-Light-64px.png', style={"width": "100%",'padding':0})]
                ,href='https://github.com/sjuanandres0/Chewbacca', target="_blank"
            ) 

            ,html.P(["Report updated: ", today], style={
                'color':'grey'
                #,'text-align':'bottom'
                ,'position':'absolute'
                ,'bottom':0
                ,'fontSize':'70%'
            })
        ], style=SIDEBAR_STYLE)#{'color':'black','background-color':'black','border':'0px dotted yellow'})
    ])
    ,html.Div(children=[
#        for strategy in chewie_pack.strategies:
            daq.Gauge(id='gauge_sg1', label='Buy and Hold', value=0, min=-5, max=5, showCurrentValue=True#, units='x'
                #,color={"gradient":True,"ranges":{"green":[0,5],"red":[-5,0]}}
        )
        ,html.Br()
        ,dcc.Graph(id='graph_strategy')
        ,html.Br()
        ,DataTable(
            id = 'datatable_signals',
            columns = d_columns_signals,
            data = df.to_dict('records'),
            cell_selectable = False,
            sort_action = 'native',
            page_action = 'native',
            page_current = 0,
            page_size = 10,
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
        #,dcc.Graph(id="graph_pct_change")
        #,html.Br()
        ,dcc.Graph(id="graph_candle")
    ], style={'background-color':'black', 'padding':'0px','margin':'0px 0px 0px 18rem'}) #style={'display':'inline-block', 'padding':'10px','width': '85%'})
], style={'background-color':'black', 'padding':'10px','margin':'0px'})


#######################################################################################################################
# CALLBACKs section

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("btn_csv", "n_clicks"),
    Input('dropdown_ticker', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date')]
    ,prevent_initial_call=True
)
def func(n_clicks, ticker_dropdown, date_1, date_2):
    df_download = df.copy(deep=True)
    df_download = df_download.loc[date_1:date_2]
    df_download = df_download[df_download['ticker']==ticker_dropdown]
    return dcc.send_data_frame(df_download.to_csv, "download.csv")

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    [Input("btn_xlsx", "n_clicks"),
    Input('dropdown_ticker', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date')]
    ,prevent_initial_call=True
)
def func(n_clicks, ticker_dropdown, date_1, date_2):
    df_download = df.copy(deep=True)
    df_download = df_download.loc[date_1:date_2]
    df_download = df_download[df_download['ticker']==ticker_dropdown]
    return dcc.send_data_frame(df_download.to_excel, "download.xlsx", sheet_name="RAW")


@app.callback(
    Output('graph_candle', 'figure'), 
    #Output('graph_pct_change', 'figure'),
    [
    #Input('rangeslider_toggle', 'value'),
    Input('dropdown_ticker', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date')
    ])
#def display_candlestick(value_range_slider, ticker_dropdown, date_1, date_2):
def display_candlestick(ticker_dropdown, date_1, date_2):
    df_plot = df.copy(deep=True)
    #if end_date == None:
    #    end_date = old_today
    #df_plot = df.loc[np.logical_and((df.index.date > date_1), (df.index.date < date_2))]
    df_plot = df_plot.loc[date_1:date_2]
    df_plot = df_plot[df_plot['ticker']==ticker_dropdown]
    
    fig_candle = go.Figure()
    fig_candle = plotly.subplots.make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7,0.10,0.15,0.10])
    fig_candle.add_trace(go.Candlestick(
        x = df_plot.index
        ,open = df_plot.Open
        ,high = df_plot.High
        ,low = df_plot.Low
        ,close = df_plot.Close
        ,name='OHLC'
    ))
    fig_candle.update_layout(
        title = '<b>{}</b>'.format(ticker_dropdown)
#        ,xaxis_rangeslider_visible='slider' in value_range_slider
        ,xaxis_rangeslider_visible=False
        ,plot_bgcolor ='black'
        ,paper_bgcolor = 'black'
        ,font = {'color':'grey'}
        ,xaxis = {'showgrid':False,'title':None}
        ,yaxis={'showgrid':True,'gridcolor':'rgb(50, 50, 50)','gridwidth':1,'zeroline':False}
        ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.07,#1.02,
            xanchor="right",
            x=1
            ,font={'color':'grey'}
            ,title='')
        ,height=900
    )
    # Add Moving Average Trace
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_10'], opacity=0.7, line=dict(color='yellow', width=2), name='SMA_10'))
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], opacity=0.7, line=dict(color='orange', width=1), name='SMA_50'))
    # Add Bolinger Bands (BB) Trace
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_10_upper'], opacity=0.7, line=dict(color='grey', width=2), name='BB_10_upper'))
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_10_lower'], opacity=0.7, line=dict(color='grey', width=2), name='BB_10_lower'))
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_50_upper'], opacity=0.7, line=dict(color='darkblue', width=2), name='BB_50_upper'))
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_50_lower'], opacity=0.7, line=dict(color='darkblue', width=2), name='BB_50_lower'))
    
    # Add Row VOLUME
    #colors = ['green' if row['Open'] - row['Close'] >= 0 else 'red' for index, row in df_plot.iterrows()]
    colors=np.where(df_plot['pct_change']<0, 'red', 'green')
    fig_candle.add_trace(go.Bar(
        x=df_plot.index
        ,y=df_plot['Volume']
        ,marker_color=colors
        ,marker_line_width=0
        ,opacity=0.8
        ,name='Volume'
        ), row=2, col=1
    )
    fig_candle.update_layout(yaxis2={'showgrid':True,'gridcolor':'rgb(50, 50, 50)','gridwidth':0.1,'title':None,'zeroline':False})

    # Add Row PCT_CHANGE
    fig_candle.add_trace(go.Bar(
        x=df_plot.index
        ,y=df_plot['pct_change'] 
        ,marker_color=np.where(df_plot['pct_change']<0, 'red', 'green')
        #,marker_line_color=np.where(df_plot['pct_change']<0, 'red', 'green')
        ,marker_line_width=0
        ,opacity=0.8
        ,name='pct_change'
        ), row=3, col=1
    )
    fig_candle.update_layout(yaxis3={'showgrid':True,'gridcolor':'rgb(50, 50, 50)','gridwidth':0.1,'title':None,'zeroline':False})

    # Add Row RSI
    fig_candle.add_trace(go.Bar(
        x=df_plot.index
        ,y=df_plot['RSI_10'] 
        ,marker_color='blue'
        #,marker_color=np.where(df_plot['pct_change']<0, 'red', 'green')
        #,marker_line_color=np.where(df_plot['pct_change']<0, 'red', 'green')
        ,marker_line_width=0
        ,opacity=0.5
        ,name='RSI_10'
        ), row=4, col=1
    )
    fig_candle.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI_50'], opacity=0.9, line=dict(color='blueviolet', width=2), name='RSI_50'), row=4, col=1)

    fig_candle.update_layout(yaxis4={'showgrid':True,'gridcolor':'rgb(50, 50, 50)','gridwidth':0.1,'title':None,'zeroline':False})

    return fig_candle #, df_plot, df_plot #, fig_pct_change


@app.callback(
    Output('datatable_signals', 'data'),
    Input('dropdown_ticker', 'value'))
def update_table(ticker_dropdown):
    df_copy = df.copy(deep=True)
    df_copy = df_copy[df_copy['ticker']==ticker_dropdown].sort_index(ascending=False).reset_index()[['Date','Close'] + chewie_pack.indicators]
    #df_copy['Date'] = datetime.date(df_copy['Date'])
    return df_copy.to_dict('records')


@app.callback(
    Output('graph_strategy', 'figure'),
    Output('datatable_strategies_stats', 'data'),
    Output('gauge_sg1', 'value'),
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
        ,font={'color':'grey'}
        ,xaxis={'showgrid':False,'gridcolor':'red','title':None}
        ,yaxis={'showgrid':True,'gridcolor':'darkgrey','title':None}
        ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.07,#1.02,
            xanchor="right",
            x=1
            ,font={'color':'grey'}
            ,title=''
        ))
    table_stats = bt_results.stats.loc[chewie_pack.stats_to_display].astype(float).round(2).reset_index().rename(columns={'index':'Stat'})
    gauge = bt_results.stats.loc['total_return']['Buy_and_Hold']
    return fig_strategies, table_stats.to_dict('records'), gauge


if __name__ == '__main__':
    app.run_server(debug=True)