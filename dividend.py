import yfinance as yf
import pandas as pd

data = pd.DataFrame()
stock_list = ['AAPL', 'MSFT','GOOG']

start = '2020-12-01'
end = '2021-12-01'

for i in stock_list:
    series = yf.Ticker(i).dividends.loc[start:end]
    data = pd.concat([data, series], axis=1)

data.columns = stock_list
print(data)