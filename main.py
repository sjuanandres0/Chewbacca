import os
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import chewie_pack
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

#bot_id = 'test'

base = pd.DataFrame()#columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'ticker', 'nom_change', 'pct_change'])
ticker_list = chewie_pack.ticker_list
indicators = chewie_pack.indicators

for ticker_lookup in ticker_list:
    ticker = yf.Ticker(ticker_lookup)
    # Get historical market data
    hist = ticker.history(start=chewie_pack.start_date).reset_index()
    hist['ticker'] = ticker_lookup
    #hist = ticker.history(period="max").reset_index()
    
    # Creating indicators
    hist['nom_change'] = round((hist['Close'].diff()), 2)
    hist['pct_change'] = round((hist['Close'].pct_change()*100), 2)
    hist['SMA_10'] = round(talib.SMA(hist['Close'], timeperiod=10), 2)
    hist['SMA_50'] = round(talib.SMA(hist['Close'], timeperiod=50), 2)
    hist['EMA_10'] = round(talib.EMA(hist['Close'], timeperiod=10), 2)
    hist['EMA_50'] = round(talib.EMA(hist['Close'], timeperiod=50), 2)
    hist['ADX_10'] = round(talib.ADX(hist['High'], hist['Low'], hist['Close'], timeperiod=10), 2)
    hist['ADX_50'] = round(talib.ADX(hist['High'], hist['Low'], hist['Close'], timeperiod=50), 2)
    hist['RSI_10'] = round(talib.RSI(hist['Close'], timeperiod=10), 2)
    hist['RSI_50'] = round(talib.RSI(hist['Close'], timeperiod=50), 2)
    hist['BB_10_upper'], hist['BB_10_middle'], hist['BB_10_lower'] = talib.BBANDS(hist['Close'], nbdevup=2, nbdevdn=2, timeperiod=10)
    hist['BB_50_upper'], hist['BB_50_middle'], hist['BB_50_lower'] = talib.BBANDS(hist['Close'], nbdevup=2, nbdevdn=2, timeperiod=50)
    hist['ADX_10'] = talib.ADX(hist['High'], hist['Low'], hist['Close'], timeperiod=50)

    # Creating signals
    hist['sg_AboveSMA_10'] = hist[['Close','SMA_10']].apply(lambda x: 'buy' if x.Close>x.SMA_10 else 'sell' if x.Close<x.SMA_10 else 'hold', axis=1)
    hist['sg_AboveSMA_50'] = hist[['Close','SMA_50']].apply(lambda x: 'buy' if x.Close>x.SMA_50 else 'sell' if x.Close<x.SMA_50 else 'hold', axis=1)
    hist['sg_AboveEMA_10'] = hist[['Close','EMA_10']].apply(lambda x: 'buy' if x.Close>x.EMA_10 else 'sell' if x.Close<x.EMA_10 else 'hold', axis=1)
    hist['sg_AboveEMA_50'] = hist[['Close','EMA_50']].apply(lambda x: 'buy' if x.Close>x.EMA_50 else 'sell' if x.Close<x.EMA_50 else 'hold', axis=1)
    hist['sg_ADX_10'] = hist['ADX_10'].map(chewie_pack.ADX_sg)
    hist['sg_ADX_50'] = hist['ADX_50'].map(chewie_pack.ADX_sg)
    hist['sg_RSI_10'] = hist['RSI_10'].apply(lambda x: 'buy' if x<25 else 'sell' if x>75 else 'hold')
    hist['sg_RSI_50'] = hist['RSI_50'].apply(lambda x: 'buy' if x<25 else 'sell' if x>75 else 'hold')
    hist['sg_BB_10'] = hist.apply(lambda x: chewie_pack.BB_func(x['Close'], x['BB_10_upper'], x['BB_10_lower']), axis=1)
    hist['sg_BB_50'] = hist.apply(lambda x: chewie_pack.BB_func(x['Close'], x['BB_50_upper'], x['BB_50_lower']), axis=1)

    base = base.append(hist, ignore_index=True)

    nom_change = hist['nom_change'].iloc[-1]
    pct_change = hist['pct_change'].iloc[-1]
    
    # Send msg if at least 1 indicator is not hold
    not_hold = (hist[indicators].iloc[-1] != 'hold').any() 
    if not_hold: 
    #if ticker_lookup == 'BTC-USD':
        cnt += 1
        up_down_symbol = ['📉' if pct_change<0 else '📈'][0] ##🔻🔼

        message = '{}. <b>{}</b> {} <code>{:,.2f} {:,.2f}%</code>'.format(cnt, ticker_lookup, up_down_symbol, nom_change, pct_change)
        signals = []
        for i, indicator in enumerate(indicators):
            signals.append(hist[indicator].iloc[-1])
            signals[i] = signals[i] + [' 🔴' if signals[i]=='sell' else ' 🟢' if signals[i]=='buy' else ''][0]
            message += '\n' + indicator + ' ' + signals[i]
        #message = '{}. <b>{}</b> {} <code>{:,.2f}%</code>\nsg_RSI_10 {}\nsg_RSI_50 {}\nsg_BB_10 {}\nsg_BB_50 {}'.format(cnt, ticker_lookup, up_down_symbol, pct_change, indicators[0],indicators[1],indicators[2],indicators[3])#sg_RSI_10, sg_RSI_50, sg_BB_10, sg_BB_50)
        api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
        requests.get(api_url)


# Save new ticker_data
#base_old = pd.read('ticker_data.csv')
base.to_csv('ticker_data.csv', index=False)
#base.to_sql(name='ticker_data', con=engine, if_exists='replace')

# Overview details
total_tickers = len(ticker_list)
total_rows = len(base)
end_tmsp = datetime.now()
elapsed_sec = (end_tmsp - start_tmsp).seconds
message = 'Ran_{}\nElapsed_{}_secs\n{}_tickers\n{}_rows\n<a href="{}">Dashboard</a>'.format(machine, elapsed_sec, total_tickers, total_rows, chewie_pack.chewie_url)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)


# End
print('main.py run complete')