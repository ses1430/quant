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

    sma120 = ta.trend.sma_indicator(t, window=120, fillna=True)[-1]
    sma200 = ta.trend.sma_indicator(t, window=200, fillna=True)[-1]

    # stat[ticker]['SMA120'] = sma120
    # stat[ticker]['SMA200'] = sma200
    stat[ticker]['SMA120'] = t[-1] / sma120
    stat[ticker]['SMA200'] = t[-1] / sma200

    stat[ticker]['RSI'] = ta.momentum.rsi(t)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(t, window, window_dev, True)[-1] * 100    

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

# export to excel file
writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")