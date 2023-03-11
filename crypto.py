import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import ta
import os

period = '10y'

# 종목
stocks = ['BTC-KRW','ETH-KRW','BTC-USD','ETH-USD']
data = yf.download(stocks, period=period, rounding=True, ignore_tz=True)
df = data['Close']

# rsi, bollinger band 계산
stat = {}
window, window_dev = 14, 2
for ticker in stocks:
    stat[ticker] = {}
    ticker_data = df[ticker]
    stat[ticker]['RSI'] = ta.momentum.rsi(ticker_data)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True)[-1] * 100

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('crypto.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("crypto.xlsx")