import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import ta
import os

period = '1y'

# 보유종목
stocks = ['^FCHI','RMS.PA','MC.PA','CDI.PA','OR.PA','KER.PA','P911.DE','7974.T']
data = yf.download(stocks, period=period, rounding=True)
df = data['Close']

# 주말도 나오게
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
    ticker_data = data['Close'][ticker]
    stat[ticker]['RSI'] = ta.momentum.rsi(ticker_data)[-1]
    stat[ticker]['BB.P'] = ta.volatility.bollinger_pband(ticker_data, window, window_dev, True)[-1]

df_stat = pd.DataFrame(data=stat)[::-1]

df = pd.concat([df, df_stat]).iloc[::-1].T
df.rename(columns={df.columns[0]:'RSI'}, inplace=True)

writer = pd.ExcelWriter('europe.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("europe.xlsx")