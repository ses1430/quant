from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
from datetime import datetime, timezone

stocks = ['RMS.PA','MC.PA','KER.PA']
df = yf.download(stocks, period='5y', interval='1d')['Close']
df = df[stocks]

writer = pd.ExcelWriter('epa.xlsx', engine='xlsxwriter')
df.iloc[::-1].to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE epa.xlsx")
