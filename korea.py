import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt
import ta
import os

stocks = {item.split('\t')[0]:item.split('\t')[1].strip() for item in open('kor_ticker.dat', 'r', encoding='utf-8').readlines()}

start_dt = (dt.datetime.now() - dt.timedelta(days=365*10+10)).strftime('%Y-%m-%d')
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

# rsi, bollinger band 계산
stat = {}
window, window_dev = 14, 2

# historical volatility 계산 함수 (새로 추가)
def calculate_historical_volatility(prices, window=20): # 기본 윈도우는 20일
    log_returns = np.log(prices / prices.shift(1)).dropna()
    daily_volatility = log_returns.rolling(window=window).std()
    annual_volatility = daily_volatility * np.sqrt(252)
    return annual_volatility.iloc[-1] # 마지막 값 반환

for ticker in data.columns:
    stat[ticker] = {}
    ticker_data = data[ticker]
    ticker_data_week = ticker_data.resample('W-FRI').last()
    ticker_data_month = ticker_data.resample('ME').last()

    # 기존 'b"' 대신 historical volatility 사용
    stat[ticker]['b"'] = calculate_historical_volatility(ticker_data, 180) * 100
    
    stat[ticker]['RSI.일'] = ta.momentum.rsi(ticker_data).iloc[-1]
    stat[ticker]['RSI.주'] = ta.momentum.rsi(ticker_data_week).iloc[-1]
    stat[ticker]['RSI.월'] = ta.momentum.rsi(ticker_data_month).iloc[-1]
    
    stat[ticker]['BB.일'] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True).iloc[-1] * 100
    stat[ticker]['BB.주'] = ta.volatility.bollinger_pband(ticker_data_week, window, window_dev, True).iloc[-1] * 100
    stat[ticker]['BB.월'] = ta.volatility.bollinger_pband(ticker_data_month, window, window_dev, True).iloc[-1] * 100

df_stat = pd.DataFrame(data=stat)[::-1]

# KODEX S&P500 기준으로 b"값 정규화
target_name = stocks['379800']
df_stat.loc['b"'] = df_stat.loc['b"'] / df_stat.loc['b"', target_name]

df = pd.concat([df, df_stat]).iloc[::-1].T

writer = pd.ExcelWriter('kdrx.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()
os.startfile("kdrx.xlsx")