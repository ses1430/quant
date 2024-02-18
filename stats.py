import yfinance as yf
import os
import pandas as pd

stats = {}
tickers = [t.strip() for t in open('ticker.txt','r').readlines()]
obj = yf.Tickers(tickers).tickers

for ticker in tickers:
    stats[ticker] = {}

    try:
        stats[ticker]['forwardPE'] = obj[ticker].info.get('forwardPE', 'n/a')
        stats[ticker]['trailingPE'] = obj[ticker].info.get('trailingPE', 'n/a')
        stats[ticker]['beta'] = obj[ticker].info.get('beta', 'n/a')
        #stats[ticker]['heldPercentInsiders'] = obj[ticker].info.get('heldPercentInsiders', 'n/a')
        #stats[ticker]['heldPercentInstitutions'] = obj[ticker].info.get('heldPercentInstitutions', 'n/a')

        print(ticker, stats[ticker]['beta'], stats[ticker]['trailingPE'])
    except KeyError as e:
        print(ticker, 'key error...')
        pass
    except TypeError as e:
        print(ticker, 'type error...')
        pass

df = pd.DataFrame(data=stats)[::-1].T

writer = pd.ExcelWriter('stats.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("stats.xlsx")