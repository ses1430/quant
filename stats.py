import yfinance as yf
import os
import pandas as pd

stats = {}
tickers = [t.strip() for t in open('ticker.txt','r').readlines() if not t.startswith('#')]
prices = yf.download(tickers, interval='1d', period='5y', rounding=True, ignore_tz=True)
obj = yf.Tickers(tickers).tickers

for ticker in tickers:
    stats[ticker] = {}
    t = prices['Close'][ticker]
    change_rate_mean = t.pct_change().abs().mean()

    try:
        info = obj[ticker].info
        stats[ticker]['forwardPE'] = info.get('forwardPE', 'n/a')
        stats[ticker]['trailingPE'] = info.get('trailingPE', 'n/a')
        stats[ticker]['beta"'] = change_rate_mean * 100
        stats[ticker]['beta'] = info.get('beta', 'n/a')
        stats[ticker]['marketCap'] = info.get('marketCap', 'n/a')  # Add market capitalization

        if stats[ticker]['marketCap'] != 'n/a':
            stats[ticker]['marketCap'] = round(stats[ticker]['marketCap'] / 1000000000, 1)

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