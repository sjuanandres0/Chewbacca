# Retrieve and update historic 5m candles

import pandas as pd
import yfinance as yf
import datetime

year = datetime.datetime.today().year
month = datetime.datetime.today().month
day = datetime.datetime.today().day
date_str = str(year)+str(month)+str(day)
date_str

tickers = ['BTC-USD','ETH-USD','ADA-USD','SOL-USD','DOT-USD','AVAX-USD','AAPL','TSLA','AMZN','AMD','TWTR','MELI','NKE','COIN'] #,'LUNA1-USD'

for i,ticker in enumerate(tickers):
    print(i,ticker)
    df_new = yf.download(tickers=ticker, period='60d', interval='5m')
    df_new.to_csv('drafts/{}_5m_60d_{}.csv'.format(date_str,ticker))
    df_hist = pd.read_csv('drafts/5m_60d_{}.csv'.format(ticker))
    df_hist = df_hist.append(df_new)
    df_hist = df_hist.drop_duplicates(subset='Datetime', keep='last')
    df_hist.to_csv('drafts/5m_60d_{}.csv'.format(ticker), index=False)
