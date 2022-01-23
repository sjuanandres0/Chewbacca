import os
import requests
import yfinance as yf

bot_id = os.environ.get('bot_id')
chat_id = os.environ.get('chat_id')
message = 'test_message'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)


ticker_list = ['BTC-USD','ETH-USD','MSFT','TSLA','GOOG','AAPL']
for ticker_lookup in ticker_list:
    ticker = yf.Ticker(ticker_lookup)
    #print(ticker.info)
    # get historical market data
    hist = ticker.history(period="max")
    #print(hist)
    #hist.to_csv('hist_'+ticker_lookup+'.csv')
    (hist['Close'].pct_change()*100).iloc[-1]
    message = 'Daily Pct change for {0:,.2f}'.format(ticker_lookup)
    api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
    requests.get(api_url)
