from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
from datetime import datetime, timezone
import ta

period, interval = '20Y', '1D'

# 보유종목
stocks = ['RMS.PA','MC.PA','CDI.PA','OR.PA','KER.PA','P911.DE']
data = yf.download(stocks, period=period, interval=interval)
df = data['Close']
df = df[stocks]

# RSI 계산
rsi = {}
for ticker in stocks:
    rsi[ticker] = ta.momentum.rsi(data['Close'][ticker])[-1]

df = pd.concat([df, pd.DataFrame(data=[rsi])]).iloc[::-1].T
df.rename(columns={df.columns[0]:'RSI'}, inplace=True)

writer = pd.ExcelWriter('europe.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE europe.xlsx")
