import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timezone, timedelta
import os

period = '20y'

# target tickers
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks]
data = yf.download(stocks, period=period, rounding=True, ignore_tz=True)
df = data['Close']

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
    t = data['Close'][ticker]
    t_week = t.resample('W-FRI').last()
    t_month = t.resample('M').last()

    sma20 = ta.trend.sma_indicator(t, window=20, fillna=True)[-1]
    sma100 = ta.trend.sma_indicator(t, window=100, fillna=True)[-1]

    stat[ticker]['SMA20'] = t[-1] / sma20
    stat[ticker]['SMA100'] = t[-1] / sma100

    stat[ticker]['RSI'] = ta.momentum.rsi(t)[-1]
    stat[ticker]['RSI.W'] = ta.momentum.rsi(t_week)[-1]
    stat[ticker]['RSI.M'] = ta.momentum.rsi(t_month)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(t, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.W'] = ta.volatility.bollinger_wband(t, window, window_dev, True)[-1]

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

# export to excel file
writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")