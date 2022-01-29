import os
import requests
import yfinance as yf
import pandas as pd
import chewie_variables as ch_var
from datetime import datetime

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

base = pd.DataFrame(columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'pct_change','ticker'])
ticker_list = ch_var.ticker_list #['BTC-USD','ETH-USD','MSFT','TSLA','GOOG','AAPL']
for ticker_lookup in ticker_list:
    ticker = yf.Ticker(ticker_lookup)
    # get historical market data
    # hist = ticker.history(period="max").reset_index()
    hist = ticker.history(start='2000-01-01').reset_index()
    hist['pct_change'] = (hist['Close'].pct_change()*100)
    hist['ticker'] = ticker_lookup
    base = base.append(hist, ignore_index=True)
    pct_change = (hist['Close'].pct_change()*100).iloc[-1]
    
    if ticker_lookup == 'BTC-USD':
        message = "{} Daily_Pct_change {:,.2f}".format(ticker_lookup, pct_change)
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