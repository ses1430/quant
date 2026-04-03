import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import ta
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

period = '5y'

# 종목
stocks = 'BTC,ETH,SOL,XRP,DOGE,ADA'
stocks = [item + '-KRW' for item in stocks.split(',')]
data = yf.download(stocks, period=period, rounding=True, ignore_tz=True)
df = data['Close'][stocks]

df.index = df.index.tz_localize(None)

# rsi, bollinger band 계산
stat = {}
window, window_dev = 14, 2
for ticker in stocks:
    stat[ticker] = {}
    ticker_data = df[ticker]
    ticker_data_week = ticker_data.resample('W-SAT').last()
    ticker_data_month = ticker_data.resample('M').last()

    stat[ticker]['RSI.일'] = ta.momentum.rsi(ticker_data)[-1]
    stat[ticker]['RSI.주'] = ta.momentum.rsi(ticker_data_week)[-1]
    stat[ticker]['RSI.월'] = ta.momentum.rsi(ticker_data_month)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True)[-1] * 100
    stat[ticker]['BB.w'] = ta.volatility.bollinger_pband(ticker_data_week, window, window_dev, True)[-1] * 100

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('crypto.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("crypto.xlsx")