import os
import requests
import yfinance as yf
import pandas as pd

bot_id = os.environ.get('bot_id')
chat_id = os.environ.get('chat_id')
if bot_id == None:
    import config.cred as cred
    bot_id = cred.bot_id
    chat_id = cred.chat_id

#message = 'test_message'
message = 'Check: https://chewbacca22.herokuapp.com/'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)

base = pd.DataFrame(columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'ticker'])
ticker_list = ['BTC-USD','ETH-USD','MSFT','TSLA','GOOG','AAPL']
for ticker_lookup in ticker_list:
    ticker = yf.Ticker(ticker_lookup)
    #print(ticker.info)
    # get historical market data
    hist = ticker.history(period="max").reset_index()
    hist['ticker'] = ticker_lookup
    base = base.append(hist, ignore_index=True)
    pct_change = (hist['Close'].pct_change()*100).iloc[-1]
    
    if ticker_lookup == 'BTC-USD':
        message = "{} Daily_Pct_change {:,.2f}".format(ticker_lookup, pct_change)
        api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
        requests.get(api_url)

#base_old = pd.read('ticker_data.csv')
#base.to_csv('Chewbacca/ticker_data.csv', index=False)
base.to_csv('ticker_data.csv', index=False)