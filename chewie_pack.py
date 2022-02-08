
# Start date for getting data
start_date='2010-01-01'

# List of tickers in scope
ticker_list_crypto = ['BTC-USD','ETH-USD','SOL-USD','ADA-USD']
ticker_list_stocks = ['^GSPC','FDX','MSFT','TSLA','GOOG','AAPL']
tickers_list_others = ['FB','NVDA','JNJ','JPM','V','PG','XOM','MA','BAC','DIS','PFE','CVX','ADBE','KO','PEP','CSCO','ABT','CRM','ACN','NFLX','WMT','INTC','QCOM','MCD','NKE','AI','T','AMD','MDT','PM','HON','GS','BLK','SBUX','CAT','DE','BKNG','MMM','GM','F','FIS','BYND','MRNA','PFE']
ticker_list = ticker_list_crypto + ticker_list_stocks # + tickers_list_others

# Chewbacca Heroku Link
chewie_url = 'https://chewbacca22.herokuapp.com/'

indicators = ['sg_AboveSMA_10','sg_AboveSMA_50','sg_AboveEMA_10','sg_AboveEMA_50', 'sg_ADX_10', 'sg_ADX_50','sg_RSI_10', 'sg_RSI_50', 'sg_BB_10', 'sg_BB_50']

def BB_func(close, upper, lower):
    '''Function to calculate if to buy, sell or hold'''
    if close<lower:
        return 'buy'
    elif close>upper:
        return 'sell'
    else:
        return 'hold'

def BHS_to_sg(BHS):
    '''[Buy, Hold, Sell] mapped to [1, 0, -1] respectively'''
    if BHS=='buy':
        return 1
    elif BHS=='hold':
        return 0
    elif BHS=='sell':   
        return -1
    else:
        return null

def ADX_sg(value):
    if value<=25:
        return 'no_trend'
    elif value<50:
        return 'trending_mkt'
    else:
        return 'strong_trending_mkt'
