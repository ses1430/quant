import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timezone, timedelta
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# target tickers
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks if not t.startswith('#')]

end_date = datetime.now()
#end_date = datetime(2025, 1, 28)
start_date = end_date - timedelta(days=10*365+10)  # 10 years ago

data = yf.download(stocks, start=start_date, end=end_date, rounding=True, ignore_tz=True)
df = data['Close']

# Convert datetime index to timezone-naive
df.index = df.index.tz_localize(None)

# make data with 365days
days = [df.index[0] + timedelta(days=i) for i in range((df.index[-1] - df.index[0]).days + 1)]
df_days = pd.DataFrame(days)
df_days.index = days

df = pd.concat([df, df_days], axis=1)
df = df.fillna(method='ffill')[stocks]

# rsi, bollinger band
stat = {}
window, window_dev = 14, 2
    
for ticker in stocks:
    stat[ticker] = {}
    t_day = data['Close'][ticker]

    # Convert datetime index to timezone-naive
    t_day.index = t_day.index.tz_localize(None)

    t_week = t_day.resample('W-FRI').last()
    t_month = t_day.resample('M').last()

    # RSI 계산
    stat[ticker]['RSI.D'] = ta.momentum.rsi(t_day)[-1]
    stat[ticker]['RSI.W'] = ta.momentum.rsi(t_week)[-1]
    stat[ticker]['RSI.M'] = ta.momentum.rsi(t_month)[-1]
    
    # 볼린저 밴드 계산
    stat[ticker]['BB.D'] = ta.volatility.bollinger_pband(t_day, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.W'] = ta.volatility.bollinger_pband(t_week, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.M'] = ta.volatility.bollinger_pband(t_month, window, window_dev, True)[-1] * 100
        
    # 이동평균선 계산 (ta.trend.sma_indicator 사용)
    current_price = t_day[-1]    
    sma60 = ta.trend.sma_indicator(t_day, window=60, fillna=True)[-1]
    sma120 = ta.trend.sma_indicator(t_day, window=120, fillna=True)[-1]
    sma200 = ta.trend.sma_indicator(t_day, window=200, fillna=True)[-1]

    # print(ticker, current_price, sma60, sma120, sma200)
    
    # 각 이평선 대비 몇 % 위에 있는지 계산
    '''
    stat[ticker]['SMA60'] = round((current_price / sma60 - 1)*100, 1)
    stat[ticker]['SMA120'] = round((current_price / sma120 - 1)*100, 1)
    stat[ticker]['SMA200'] = round((current_price / sma200 - 1)*100, 1)
    '''

df_stat = pd.DataFrame(data=stat, dtype='float64')[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

# export to excel file
writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")