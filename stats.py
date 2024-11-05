import yfinance as yf
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import OrderedDict

def read_tickers(filename):
    with open(filename, 'r') as file:
        return [t.strip() for t in file if not t.startswith('#')]

def get_stock_data(tickers):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)  # 5 years ago
    return yf.download(tickers, start=start_date, end=end_date, interval='1d', rounding=True, ignore_tz=True)

def calculate_stats(prices, obj, tickers):
    stats = OrderedDict()
    basis_change_rate = None
    for ticker in tickers:
        stats[ticker] = OrderedDict({
            'forwardPE': '',
            'trailingPE': '',            
            'beta"': '',
            'beta': '',
            'marketCap': '',
        })
        
        if ticker not in prices['Close'].columns:
            print(f"Warning: No data found for {ticker}")
            continue
        
        t = prices['Close'][ticker]
        change_rate_mean = t.pct_change().abs().mean()
        
        info = obj[ticker].info
        stats[ticker].update({
            'marketCap': round(info.get('marketCap', 0) / 1e9, 1) if info.get('marketCap') not in ['', None] else '',
            'beta': info.get('beta', ''),
            'beta"': change_rate_mean * 100,
            'trailingPE': info.get('trailingPE', ''),
            'forwardPE': info.get('forwardPE', ''),
        })
        
        if ticker == '^GSPC':
            basis_change_rate = change_rate_mean * 100
        
        print(f"{ticker}: beta = {stats[ticker]['beta']}, trailingPE = {stats[ticker]['trailingPE']}")
    
    return stats, basis_change_rate

def normalize_beta(stats, basis_change_rate):
    if basis_change_rate is None or basis_change_rate == 0:
        print("Warning: Unable to normalize beta due to invalid basis_change_rate")
        return stats

    for ticker in stats:
        if isinstance(stats[ticker]['beta"'], (int, float)):
            stats[ticker]['beta"'] /= basis_change_rate
        else:
            stats[ticker]['beta"'] = ''
    return stats

def save_to_excel(stats):
    df = pd.DataFrame.from_dict(stats, orient='index')
    df = df[df.columns[::-1]]  # Reverse the column order
    with pd.ExcelWriter('stats.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1')
    os.startfile("stats.xlsx")

def main():
    tickers = read_tickers('ticker.txt')
    #tickers = read_tickers('all_tickers.csv')
    prices = get_stock_data(tickers)
    obj = yf.Tickers(tickers).tickers
    
    try:
        stats, basis_change_rate = calculate_stats(prices, obj, tickers)
        stats = normalize_beta(stats, basis_change_rate)
        save_to_excel(stats)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    