from functools import total_ordering
import yfinance as yf
import pandas as pd
import subprocess
import ta
from datetime import datetime, timezone, timedelta
import os
import sys

stocks = [t.strip() for t in open('ticker.txt','r').readlines()]
tickers = yf.Tickers(stocks).tickers
stats = {}

for stock in stocks:
    stats[stock] = {}
    print(stock, '...')
    
    try:
        info = tickers[stock].stats()
        stats[stock]['Beta']    = info['defaultKeyStatistics']['beta']
        stats[stock]['P/E']     = info['summaryDetail']['trailingPE']
        stats[stock]['Fwd P/E'] = info['summaryDetail']['forwardPE']
    except KeyError as e:
        pass

df = pd.DataFrame(data=stats)[::-1].T

writer = pd.ExcelWriter('stats.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("stats.xlsx")