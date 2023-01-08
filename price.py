from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
import ta
from datetime import datetime, timezone, timedelta
import os
import sys

period, interval, prepost = '1y', '1d', False
if len(sys.argv) > 1 and sys.argv[1] == '1':
    print('prepost true')
    prepost = True

# 보유종목
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks]
data = yf.download(stocks, period=period, interval=interval, prepost=prepost)

# 종가만 추출
df = data['Close']

# 휴일도 나오게
days = [df.index[0] + timedelta(days=i) for i in range((df.index[-1] - df.index[0]).days + 1)]
df_days = pd.DataFrame(days)
df_days.index = days

df = pd.concat([df, df_days], axis=1)
df = df.fillna(method='ffill')[stocks]

# rsi, bollinger band 계산
stat = {}
window, window_dev = 14, 2

for ticker in stocks:
    stat[ticker] = {}
    t = data['Close'][ticker]
    stat[ticker]['RSI'] = ta.momentum.rsi(t)[-1]
    stat[ticker]['BB.L'] = ta.volatility.bollinger_lband(t, window, window_dev, True)[-1]
    stat[ticker]['BB.H'] = ta.volatility.bollinger_hband(t, window, window_dev, True)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(t, window, window_dev, True)[-1]

df_stat = pd.DataFrame(data=stat)[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")