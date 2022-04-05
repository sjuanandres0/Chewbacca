import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import yfinance as yf

#Init
start_tmsp = datetime.now()
bot_id = os.environ.get('bot_id')
chat_id = os.environ.get('chat_id')
machine = 'server'
if bot_id == None:
    import config.cred as cred
    bot_id = cred.bot_id
    chat_id = cred.chat_id
    machine = 'laptop'
message = 'Start {}'.format(start_tmsp)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
#requests.get(api_url)

#Setup
tds = pd.read_csv('tds.csv') 
ticker = 'BTC-USD'
strategy='cb1'
thresh_rsi_in=25
thresh_rsi_cond2=30
thresh_tp=0.009
thresh_sl=-0.049
qty_in=100

def rsi(df, close_name, periods = 14, ema = True):
    '''
    Returns a pd.Series with the Relative Strength Index.
    '''
    close_delta = df[close_name].diff()
    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    if ema == True:
        # Use exponential moving average
        ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window = periods).mean()
        ma_down = down.rolling(window = periods).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi

#while True:
#    df = yf.download(tickers=ticker, period='1d', interval='5m')
testing_df=pd.read_csv('BTC-USD_5m_60d_20220404',index_col='Datetime')
for row in range(25,len(testing_df)):
    #print('row: ',row)
    df=testing_df.iloc[0:row]

    rsi_14 = rsi(df, 'Close', periods=14)
    price_now=df.Close[-1]
    rsi_now=rsi_14[-1]
    fg1=len(tds[(tds.ticker==ticker) & (tds.strategy==strategy)]) #Hay trades?
    fg2=len(tds[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull())]) #Hay trades abiertos? (0 todo cerrado)

    if rsi_now<thresh_rsi_in:
        if fg1==0: #BUY 1st time / Open first position
            new_row=[ticker,strategy,df.index[-1],price_now,qty_in,rsi_now,0,np.nan,np.nan,np.nan,np.nan,np.nan]
            tds.loc[len(tds)] = new_row
            print('{} buy1 fg1:{} fg2:{} rsi_now:{} price_now:{}'.format(row,fg1,fg2,rsi_now,price_now))
        elif fg2==0: #BUY AFTER 1st time / Open subsequent positions
            cond2 = tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy), 'cond2'].values[-1]
            if cond2>0:
                new_row=[ticker,strategy,df.index[-1],price_now,qty_in,rsi_now,0,np.nan,np.nan,np.nan,np.nan,np.nan]
                tds.loc[len(tds)] = new_row
                print('{} buy2 fg1:{} fg2:{} cond2:{} rsi_now:{} price_now:{}'.format(row,fg1,fg2,cond2,rsi_now,price_now))
                fg2 = 1
            #print('new_row:\t',new_row)

    #if fg1>0 & fg2==0: #UPDATE cond2
    #    cond2 = tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy), 'cond2'].values[-1]
    #    print('rsi_now {} T/F {} cond2 {}'.format(rsi_now,(rsi_now>thresh_rsi_cond2),cond2))
    #fg2=len(tds[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull())]) #Hay trades abiertos?
    if ((rsi_now>thresh_rsi_cond2) & (fg1>0) & (fg2==0)): #UPDATE cond2
        cond2 = tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy), 'cond2'].values[-1]
        cond2_id = tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy), 'cond2'].index[-1]
        #print('UPDATE cond2!!!!!: ',cond2)
        cond2 = cond2+1
        #tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()) , 'cond2'] = cond2
        tds.iloc[cond2_id, 6] = cond2
        print('{} U-cond2 fg1:{} fg2:{} cond2:{} rsi_now:{} price_now:{}'.format(row,fg1,fg2,cond2,rsi_now,price_now))

    if fg2==1: #SELL?? / Already IN an Open Position
        #old_price_in = tds[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull())]['price_in'][1]
        old_price_in = tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'price_in'].values[-1]
        #old_price_in=30000
        delta = (price_now / old_price_in) - 1
        #print('delta',delta)
        if ((delta>thresh_tp) | (delta<thresh_sl)): # SELL at TP/SL
            print('{} Sell fg1:{} fg2:{} delta:{} rsi_now:{} price_now:{}'.format(row,fg1,fg2,delta,rsi_now,price_now))
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'tmstp_out'] = df.index[-1]
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'price_out'] = price_now
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'qty_out'] = 1
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'rsi_out'] = rsi_now
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'pl'] = ((price_now-old_price_in)/old_price_in)*qty_in


    #time.sleep(5)#300)
    end_tmsp = datetime.now()
    elapsed_sec = (end_tmsp - start_tmsp).seconds
    #print(elapsed_sec, '-', end_tmsp)
    #print('fg1:',fg1)
    #print('fg2:',fg2)
    #print('rsi_now:',rsi_now)

    #tds.to_csv('tds.csv', index=False)
    #if elapsed_sec>30:#3600:
    #    break

tds.to_csv('tds.csv', index=False)
message = 'Ran {}\nElapsed {}secs\nEnd_tmsp {}'.format(machine, elapsed_sec, end_tmsp)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)
