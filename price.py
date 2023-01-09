from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
import ta
from datetime import datetime, timezone, timedelta
import os

period, interval = '20y', '1d'

# 보유종목
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks]
data = yf.download(stocks, period=period, interval=interval, prepost=True)

# 종가만 추출
df = data['Close']

# 휴일도 나오게
days = [df.index[0] + timedelta(days=i) for i in range((df.index[-1] - df.index[0]).days + 1)]
df_days = pd.DataFrame(days)
df_days.index = days

df = pd.concat([df, df_days], axis=1)
df = df.fillna(method='ffill')[stocks]

# RSI 계산
rsi = {}
for ticker in stocks:
    rsi[ticker] = ta.momentum.rsi(data['Close'][ticker])[-1]
df_rsi = pd.DataFrame(data=[rsi])

df = pd.concat([df, df_rsi]).iloc[::-1].T
df.rename(columns={df.columns[0]:'RSI'}, inplace=True)

writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("price.xlsx")