import bt

# Start date for getting data
start_date='2010-01-01'

# List of tickers in scope
ticker_list_crypto = ['BTC-USD','ETH-USD','SOL-USD','ADA-USD']
ticker_list_stocks = ['^GSPC','FDX','MSFT','TSLA','GOOG','AAPL']
tickers_list_others = ['FB','NVDA','JNJ','JPM','V','PG','XOM','MA','BAC','DIS','PFE','CVX','ADBE','KO','PEP','CSCO','ABT','CRM','ACN','NFLX','WMT','INTC','QCOM','MCD','NKE','AI','T','AMD','MDT','PM','HON','GS','BLK','SBUX','CAT','DE','BKNG','MMM','GM','F','FIS','BYND','MRNA','PFE']
ticker_list = ticker_list_crypto + ticker_list_stocks # + tickers_list_others

# Chewbacca Heroku Link
chewie_url = 'https://chewbacca22.herokuapp.com/'

# List of Indicators
indicators = ['sg_SMA_Cross','sg_EMA_Cross','sg_ADX_10','sg_ADX_50','sg_RSI_10','sg_RSI_50','sg_BB_10','sg_BB_50']
# List of Strategies
strategies = ['Buy_and_Hold','sg_SMA_Cross','sg_EMA_Cross','sg_RSI_10','sg_RSI_50','sg_BB_10','sg_BB_50']


def BB_func(close, upper, lower):
    '''Function to calculate if to buy, sell or hold with Bolinger Bands'''
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
        return None

def ADX_sg(value):
    '''Maps the ADX to trend values'''
    if value<=25:
        return 'no_trend'
    elif value<50:
        return 'trending_mkt'
    else:
        return 'strong_trending_mkt'


#### Benchmarking example
def buy_and_hold(df, ticker, signal_name, start='2020-01-01', end='2021-12-31'):
    # Get the data
    close = df.loc[(df.ticker==ticker) & (df.index>start) & (df.index<end)]['Close'].to_frame()
    # Define the benchmark strategy
    bt_strategy = bt.Strategy(signal_name,
        [bt.algos.RunOnce(),
        bt.algos.SelectAll(),
        bt.algos.WeighEqually(),
        bt.algos.Rebalance()])
    # Return the backtest
    return bt.Backtest(bt_strategy, close)

#### Strategy Optimization Signal or MA Crossover
def signal_trend(df, ticker, signal_name, start='2020-01-01', end='2021-12-31'):
    close = df.loc[(df.ticker==ticker) & (df.index>start) & (df.index<end)]['Close'].to_frame()
    signal = df.loc[(df.ticker==ticker) & (df.index>start) & (df.index<end)][signal_name]
    signal = signal.apply(BHS_to_sg).to_frame(name='Close')
    # Define the signal-based strategy
    bt_strategy = bt.Strategy(signal_name,
        [bt.algos.SelectWhere(signal),
        bt.algos.WeighEqually(),
        bt.algos.Rebalance()])
    return bt.Backtest(bt_strategy, close)

#### Strategy Optimization RSI-based Mean Reversion
def signal_rever(df, ticker, signal_name, start='2020-01-01', end='2021-12-31'):
    close = df.loc[(df.ticker==ticker) & (df.index>start) & (df.index<end)]['Close'].to_frame()
    signal = df.loc[(df.ticker==ticker) & (df.index>start) & (df.index<end)][signal_name]
    signal = signal.apply(BHS_to_sg).to_frame(name='Close')    
    # Define the signal-based strategy
    bt_strategy = bt.Strategy(signal_name,
                 [bt.algos.WeighTarget(signal), 
                bt.algos.Rebalance()]) 
    return bt.Backtest(bt_strategy, close)

#### All strategies
def strategies_eval(df, ticker, start, end):
    benchmark = buy_and_hold(df=df, ticker=ticker, signal_name='Buy_and_Hold', start=start, end=end)
    sg_SMA_Cross = signal_trend(df=df, ticker=ticker, signal_name='sg_SMA_Cross', start=start, end=end)
    sg_EMA_Cross = signal_trend(df=df, ticker=ticker, signal_name='sg_EMA_Cross', start=start, end=end)
    sg_RSI_10 = signal_rever(df=df, ticker=ticker, signal_name='sg_RSI_10', start=start, end=end)
    sg_RSI_50 = signal_rever(df=df, ticker=ticker, signal_name='sg_RSI_50', start=start, end=end)
    sg_BB_10 = signal_rever(df=df, ticker=ticker, signal_name='sg_BB_10', start=start, end=end)
    sg_BB_50 = signal_rever(df=df, ticker=ticker, signal_name='sg_BB_50', start=start, end=end)
    bt_results = bt.run(benchmark, sg_SMA_Cross, sg_EMA_Cross, sg_RSI_10, sg_RSI_50, sg_BB_10, sg_BB_50)
    return bt_results #.plot(title='Strategies for {}'.format(ticker))

stats_to_display = ['total_return', 'cagr', 'max_drawdown', 'calmar',
       'daily_sharpe', 'daily_sortino', 'daily_mean', 'daily_vol', 'daily_skew', 'daily_kurt', 
       'best_day', 'worst_day', 
       'monthly_sharpe', 'monthly_sortino', 'monthly_mean', 'monthly_vol', 'monthly_skew', 'monthly_kurt', 
       'best_month', 'worst_month', 
       'avg_drawdown', 'avg_drawdown_days', 'avg_up_month', 'avg_down_month']
