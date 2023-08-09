import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import ta
import os

period = '10y'

# 종목
stocks = 'BTC,ETH'
stocks = [item + '-KRW' for item in stocks.split(',')]
data = yf.download(stocks, period=period, rounding=True, ignore_tz=True)
df = data['Close'][stocks]

# rsi, bollinger band 계산
stat = {}
window, window_dev = 14, 2
for ticker in stocks:
    stat[ticker] = {}
    ticker_data = df[ticker]
    ticker_data_week = ticker_data.resample('W-SAT').last()
    ticker_data_month = ticker_data.resample('M').last()

    stat[ticker]['rsi'] = ta.momentum.rsi(ticker_data)[-1]
    stat[ticker]['rsi.w'] = ta.momentum.rsi(ticker_data_week)[-1]
    stat[ticker]['rsi.m'] = ta.momentum.rsi(ticker_data_month)[-1]
    stat[ticker]['bb.p'] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True)[-1] * 100
    stat[ticker]['bb.w'] = ta.volatility.bollinger_pband(ticker_data_week, window, window_dev, True)[-1] * 100

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('crypto.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("crypto.xlsx")