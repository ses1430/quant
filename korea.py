import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt
import subprocess
import ta
import os

stocks = {item.split('\t')[0]:item.split('\t')[1].strip() for item in open('kor_ticker.dat', 'r', encoding='utf-8').readlines()}

start_dt = (dt.datetime.now() - dt.timedelta(days=365*5+10)).strftime('%Y-%m-%d')
end_dt = dt.datetime.now().strftime('%Y-%m-%d')

df_list = [fdr.DataReader(t, start_dt, end_dt)['Close'] for t in stocks]
data = pd.concat(df_list, axis=1)
data.columns = list(stocks.values())

# 주말도 나오게
days = [data.index[0] + dt.timedelta(days=i) for i in range((data.index[-1] - data.index[0]).days + 1)]
df_days = pd.DataFrame(days)
df_days.index = days

df = pd.concat([data, df_days], axis=1)
df = df.fillna(method='ffill')[list(stocks.values())]

rsi = {}
for column in data.columns:
    rsi[column] = ta.momentum.rsi(data[column])[-1]
df_rsi = pd.DataFrame(data=[rsi])

# rsi, bollinger band 계산
rsi, lband, hband, pband = {}, {}, {}, {}
window, window_dev = 14, 2

for ticker in data.columns:
    ticker_data = data[ticker]
    rsi[ticker] = ta.momentum.rsi(ticker_data)[-1]
    lband[ticker] = ta.volatility.bollinger_lband(ticker_data, window, window_dev, True)[-1]
    hband[ticker] = ta.volatility.bollinger_hband(ticker_data, window, window_dev, True)[-1]
    pband[ticker] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True)[-1]

df_stat = pd.DataFrame(data=[rsi, lband, hband, pband], index=['RSI','LBAND','HBAND','PBAND'])[::-1]
df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('kdrx.xlsx', engine='xlsxwriter')

#최근 120일치만 가져오기
df.to_excel(writer, sheet_name='Sheet1')
writer.close()
os.startfile("kdrx.xlsx")