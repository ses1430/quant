import yfinance as yf
import pandas as pd
import os
import warnings
from datetime import datetime, timedelta

warnings.simplefilter(action='ignore', category=FutureWarning)

# target tickers
stocks = open('screen.txt', 'r').readlines()
stocks = [t.strip() for t in stocks if not t.startswith('#')]
data = yf.download(stocks, interval='1d', period='max', rounding=True, ignore_tz=True)
df = data['Close']

# Filter data for the last 15 years
start_date = df.index[-1] - timedelta(days=15*365+5)
df = df[df.index >= start_date]

# Convert datetime index to timezone-naive
df.index = df.index.tz_localize(None)

# Calculate annual returns (2010-2024)
annual_returns = {}
for year in range(2010, 2025):
    year_data = df[df.index.year == year]
    if not year_data.empty and len(year_data) > 1:
        annual_returns[year] = (year_data.iloc[-1] / year_data.iloc[0] - 1) * 100
    else:
        annual_returns[year] = None
annual_returns_df = pd.DataFrame(annual_returns)

# Calculate CAGR for 1, 3, 5, and 10 years
cagr_periods = [1, 3, 5, 10]
cagr_data = {}
latest_date = df.index[-1]
for period in cagr_periods:
    start_date = latest_date - timedelta(days=period * 365)
    start_data = df[df.index >= start_date]
    valid_tickers = start_data.notna().all()
    cagr_values = ((df.iloc[-1] / start_data.iloc[0]) ** (1 / period) - 1) * 100
    cagr_data[period] = cagr_values.where(valid_tickers, None)
cagr_df = pd.DataFrame(cagr_data)

# Combine annual returns and CAGR
performance_df = pd.concat([annual_returns_df, cagr_df], axis=1)
performance_df.columns = [str(y) + 'y' for y in range(2010, 2025)] + [str(p) for p in cagr_periods]

# Export to Excel
output_file = 'screen.xlsx'
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    performance_df.to_excel(writer, sheet_name='Performance')  # Store annual returns and CAGR

# Open the file
os.startfile(output_file)
