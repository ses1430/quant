import yfinance as yf
import os
import pandas as pd

stats = {}
tickers = [t.strip() for t in open('ticker.txt','r').readlines()]
prices = yf.download(tickers, interval='1d', period='5y', rounding=True, ignore_tz=True)
obj = yf.Tickers(tickers).tickers

for ticker in tickers:
    stats[ticker] = {}
    t = prices['Close'][ticker]
    change_rate_mean = t.pct_change().abs().mean()

    try:
        stats[ticker]['forwardPE'] = obj[ticker].info.get('forwardPE', 'n/a')
        stats[ticker]['trailingPE'] = obj[ticker].info.get('trailingPE', 'n/a')
        stats[ticker]['beta"'] = change_rate_mean * 100
        stats[ticker]['beta'] = obj[ticker].info.get('beta', 'n/a')

        print(ticker, stats[ticker]['beta'], stats[ticker]['trailingPE'])
    except KeyError as e:
        print(ticker, 'key error...')
        pass
    except TypeError as e:
        print(ticker, 'type error...')
        pass

basis_change_rate = stats['^GSPC']['beta"']
for ticker in tickers:
    stats[ticker]['beta"'] = stats[ticker]['beta"'] / basis_change_rate

df = pd.DataFrame(data=stats)[::-1].T

writer = pd.ExcelWriter('stats.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("stats.xlsx")