import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import yfinance as yf


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

tds = pd.read_csv('tds.csv') 
ticker = 'BTC-USD'
strategy='cb1'
thresh_rsi=25
thresh_tp=0.009
thresh_sl=-0.0049
qty_in=100

def rsi(df, close_name, periods = 14, ema = True):
    """
    Returns a pd.Series with the relative strength index.
    """
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

df = yf.download(tickers=ticker, period='1d', interval='5m')
rsi_14 = rsi(df, 'Close', periods=14)
if rsi_14[-1]<thresh_rsi:
    price_in=df.Close[-1]
    if len(tds[(tds.ticker==ticker) & (tds.strategy==strategy)] & (tds.pl.isnull()))==0: #BUY
        new_row=[ticker,strategy,df.index[-1],price_in,qty_in,rsi_14[-1],0,np.nan,np.nan,np.nan,np.nan,np.nan]
        tds.loc[len(tds)] = new_row
        #print('new_row:\t',new_row)
    else: #Already IN an Open Position
        old_price_in = tds[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull())]['price_in'][0]
        delta = (price_in / old_price_in) - 1
        cond2 = tds[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull())]['cond2'][0]
        if rsi_14[-1]>=30: #UPDATE cond2
            cond2 += 1
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'cond2'] = cond2
            print('cond2:\t',cond2)
        print('cond2:\t',cond2)
        print('delta:\t',delta)
        if (cond2>0) & ((delta<thresh_tp) | (delta<thresh_sl)): # SELL at TP/SL
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'tmstp_out'] = df.index[-1]
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'price_out'] = df.Close[-1]
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'qty_out'] = 1
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'rsi_out'] = rsi_14[-1]
            tds.loc[(tds.ticker==ticker) & (tds.strategy==strategy) & (tds.pl.isnull()), 'pl'] = (df.Close[-1] / price_in)*qty_in

#    time.sleep(300)
end_tmsp = datetime.now()
elapsed_sec = (end_tmsp - start_tmsp).seconds
#    print(elapsed_sec, '-', end_tmsp)

#    if elapsed_sec>3600:
#        break

tds.to_csv('tds.csv', index=False)

message = 'Ran {}\nElapsed {}secs\nEnd_tmsp {}'.format(machine, elapsed_sec, end_tmsp)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)
