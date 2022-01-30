import os
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import chewie_variables as ch_var
from datetime import datetime
import talib

start_tmsp = datetime.now()

bot_id = os.environ.get('bot_id')
chat_id = os.environ.get('chat_id')
machine = 'server'
if bot_id == None:
    import config.cred as cred
    bot_id = cred.bot_id
    chat_id = cred.chat_id
    machine = 'laptop'

#message = 'test_message'
#message = 'Running Main...'#\nCheck: {}'.format(chewie_url)
#api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
#requests.get(api_url)

# BB Basic Rules
def BB_func(close, upper, middle, lower):
    if close<lower:
        return 'buy'
    elif close>upper:
        return 'sell'
    else:
        return 'hold'

base = pd.DataFrame(columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'pct_change','ticker'])
ticker_list = ch_var.ticker_list #['BTC-USD','ETH-USD','MSFT','TSLA','GOOG','AAPL']
for ticker_lookup in ticker_list:
    ticker = yf.Ticker(ticker_lookup)
    # get historical market data
    # hist = ticker.history(period="max").reset_index()
    hist = ticker.history(start='2000-01-01').reset_index()
    hist['pct_change'] = (hist['Close'].pct_change()*100)
    hist['SMA_10'] = talib.SMA(hist['Close'], timeperiod=10)
    hist['SMA_50'] = talib.SMA(hist['Close'], timeperiod=50)
    hist['EMA_10'] = talib.EMA(hist['Close'], timeperiod=10)
    hist['EMA_50'] = talib.EMA(hist['Close'], timeperiod=50)
    hist['RSI_10'] = talib.RSI(hist['Close'], timeperiod=10)
    hist['RSI_50'] = talib.RSI(hist['Close'], timeperiod=50)
    hist['BB_10_upper'], hist['BB_10_middle'], hist['BB_10_lower'] = talib.BBANDS(hist['Close'], 
        nbdevup=2,
        nbdevdn=2,
        timeperiod=10)
    hist['BB_50_upper'], hist['BB_50_middle'], hist['BB_50_lower'] = talib.BBANDS(hist['Close'], 
        nbdevup=2,
        nbdevdn=2,
        timeperiod=50)
    hist['sg_RSI_10'] = hist['RSI_10'].apply(lambda x: 'buy' if x<25 else 'sell' if x>75 else 'hold')
    hist['sg_RSI_50'] = hist['RSI_50'].apply(lambda x: 'buy' if x<25 else 'sell' if x>75 else 'hold')
    hist['sg_BB_10'] = hist.apply(lambda x: BB_func(x['Close'], x['BB_10_upper'], x['BB_10_middle'], x['BB_10_lower']), axis=1)
    hist['sg_BB_50'] = hist.apply(lambda x: BB_func(x['Close'], x['BB_50_upper'], x['BB_50_middle'], x['BB_50_lower']), axis=1)

    hist['ticker'] = ticker_lookup
    base = base.append(hist, ignore_index=True)
    pct_change = (hist['Close'].pct_change()*100).iloc[-1]
    
    if ticker_lookup == 'BTC-USD':
        message = "{}\nDaily_Pct_change {:,.2f}\nsg_RSI_10 {}\nsg_RSI_50 {}\nsg_BB_10 {}\nsg_BB_50 {}".format(ticker_lookup, pct_change, hist['sg_RSI_10'].iloc[-1], hist['sg_RSI_50'].iloc[-1], hist['sg_BB_10'].iloc[-1], hist['sg_BB_50'].iloc[-1])
        api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
        requests.get(api_url)


# Save new ticker_data
#base_old = pd.read('ticker_data.csv')
base.to_csv('ticker_data.csv', index=False)

# Overview details
total_tickers = len(ticker_list)
total_rows = len(base)
end_tmsp = datetime.now()
elapsed_sec = (end_tmsp - start_tmsp).seconds
message = 'Run completed.\nMachine: {}.\nElapsed time: {} seconds.\nTotal tickers: {}.\nTotal rows: {}.\nCheck: {}'.format(machine, elapsed_sec, total_tickers, total_rows, ch_var.chewie_url)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)

# End