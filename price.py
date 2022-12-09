from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
import ta
from datetime import datetime, timezone

period, interval = '5y', '1d'
#period, interval = '1d', '15m'

# 보유종목
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks]
data = yf.download(stocks, period=period, interval=interval)
df = data['Close']
df = df[stocks]

# RSI 계산
rsi = {}
for ticker in stocks:
    rsi[ticker] = ta.momentum.rsi(data['Close'][ticker])[-1]

df = pd.concat([df, pd.DataFrame(data=[rsi])]).iloc[::-1].T
df.rename(columns={df.columns[0]:'RSI'}, inplace=True)

writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

# subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE price.xlsx")
subprocess.call("C:\\Program Files\\Microsoft Office 15\\root\\office15\\EXCEL.EXE price.xlsx")