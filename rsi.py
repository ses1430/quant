import yfinance as yf
import ta

data = yf.download(['KRBN'], start='2021-04-01')
rsi = ta.momentum.rsi(data['Close'], window=14)
print(rsi[-1])