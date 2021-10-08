from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess

tickers = ['AAPL','ASML','KO','KRBN','LIT','MSFT','O','QQQ','SBUX','TQQQ','TSLA','WM','LMT','SOXX','SMH','RTX','NKE'
           ,'DIS','V','GOOGL','MCD','AMZN','NFLX','BOTZ','NVDA','SKYY','SOXL','QLD']

tickers = [t.strip() for t in tickers]
df = yf.download(tickers, period="120d", interval="1d")['Close']
df.fillna(method='ffill', inplace=True, axis=0)
writer = pd.ExcelWriter('price.xlsx', engine='xlsxwriter')
df.iloc[::-1].to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE price.xlsx")