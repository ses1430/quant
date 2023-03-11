from yahooquery import Ticker
import os
import pandas as pd

tickers = [t.strip() for t in open('ticker.txt','r').readlines()]
key_stats = Ticker(tickers).key_stats
stats = {}

for ticker in key_stats:
    stats[ticker] = {}
    print(ticker, '...')
    
    try:
        stats[ticker]['beta'] = key_stats[ticker]['beta']
    except KeyError as e:
        pass
    except TypeError as e:
        pass

df = pd.DataFrame(data=stats)[::-1].T

writer = pd.ExcelWriter('stats.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("stats.xlsx")