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
data = yf.download(stocks, interval='1d', period='max', rounding=True, ignore_tz=True)
df = data['Close']

# Filter data for the last 20 years
start_date = df.index[-1] - timedelta(days=10*365+5)
df = df[df.index >= start_date]

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

    stat[ticker]['RSI.일'] = ta.momentum.rsi(t_day)[-1]
    stat[ticker]['RSI.주'] = ta.momentum.rsi(t_week)[-1]
    stat[ticker]['RSI.월'] = ta.momentum.rsi(t_month)[-1]
    stat[ticker]['BB.일'] = ta.volatility.bollinger_pband(t_day, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.주'] = ta.volatility.bollinger_pband(t_week, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.월'] = ta.volatility.bollinger_pband(t_month, window, window_dev, True)[-1] * 100

df_stat = pd.DataFrame(data=stat, dtype='float64')[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

# export to excel file
writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")