import os
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import chewie_variables as ch_var
from datetime import datetime
import talib

from sqlalchemy import create_engine
engine = create_engine('sqlite:///data.db')

start_tmsp = datetime.now()
cnt = 0
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
    
    # Send msg if at least 1 indicator is not hold
    indicators = ['sg_RSI_10', 'sg_RSI_50', 'sg_BB_10', 'sg_BB_50']
    not_hold = (hist[indicators].iloc[-1] != 'hold').any() 
    if not_hold: 
    #if ticker_lookup == 'BTC-USD':
        cnt += 1
        up_down_symbol = ['📉' if pct_change<0 else '📈'][0]
        # Consider doing a for each indicator
        for i,indicator in enumerate(indicators):
            indicators[i] = hist[indicator].iloc[-1]
            indicators[i] = indicators[i] + [' 🔴' if indicators[i]=='sell' else ' 🟢' if indicators[i]=='buy' else ''][0]
        #sg_RSI_10 = hist['sg_RSI_10'].iloc[-1]
        #sg_RSI_50 = hist['sg_RSI_50'].iloc[-1]
        #sg_BB_10 = hist['sg_BB_10'].iloc[-1]
        #sg_BB_50 = hist['sg_BB_50'].iloc[-1]
        message = '{}. <b>{}</b> {} <code>{:,.2f}%</code>\nsg_RSI_10 {}\nsg_RSI_50 {}\nsg_BB_10 {}\nsg_BB_50 {}'.format(cnt, ticker_lookup, up_down_symbol, pct_change, indicators[0],indicators[1],indicators[2],indicators[3])#sg_RSI_10, sg_RSI_50, sg_BB_10, sg_BB_50)
        api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
        requests.get(api_url)


# Save new ticker_data
#base_old = pd.read('ticker_data.csv')
base.to_csv('ticker_data.csv', index=False)
base.to_sql(name='ticker_data', con=engine, if_exists='replace')

# Overview details
total_tickers = len(ticker_list)
total_rows = len(base)
end_tmsp = datetime.now()
elapsed_sec = (end_tmsp - start_tmsp).seconds
message = 'Ran_{}\nElapsed_{}_secs\n{}_tickers\n{}_rows\n<a href="{}">Dashboard</a>'.format(machine, elapsed_sec, total_tickers, total_rows, ch_var.chewie_url)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)


# End