from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
from datetime import datetime, timezone

period, interval = '5d', '1d'
#period, interval = '1d', '15m'

# 보유종목
stocks = open('ticker.txt','r').readlines()
stocks = [t.strip() for t in stocks]
df = yf.download(stocks, period=period, interval=interval)['Close']
df = df[stocks]

writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.iloc[::-1].to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE price.xlsx")

