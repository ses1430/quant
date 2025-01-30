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
    start_date = end_date - timedelta(days=365)  # 1년 전 데이터
    return yf.download(tickers, start=start_date, end=end_date, interval='1d', rounding=True, ignore_tz=True)

def calculate_stats(prices, obj, tickers):
    stats = OrderedDict()
    sp500_change_rate = None  # S&P500 지수의 변동율 저장용

    # S&P500 지수의 변동율 계산
    if '^GSPC' in prices['Close'].columns:
        sp500_prices = prices['Close']['^GSPC']
        sp500_change_rate = sp500_prices.pct_change()  # S&P500 일일 변동율

    for ticker in tickers:
        stats[ticker] = OrderedDict({
            'forwardPE': '',
            'trailingPE': '',            
            'beta"': '',  # 이제 S&P500과의 일일 변동율 차이의 평균
            'beta': '',
            'marketCap': '',
        })
        
        if ticker not in prices['Close'].columns:
            print(f"Warning: No data found for {ticker}")
            continue
        
        # 주식의 변동율 계산
        stock_prices = prices['Close'][ticker]
        stock_change_rate = stock_prices.pct_change()  # 주식 일일 변동율

        # S&P500과의 변동율 차이 계산
        if sp500_change_rate is not None:
            # 주식과 S&P500의 일일 변동율 차이 계산
            diff_change_rate = (stock_change_rate - sp500_change_rate).dropna()  # NaN 제거
            beta_diff_mean = diff_change_rate.abs().mean() * 100  # 차이값 절대값 평균 (백분율)
        else:
            beta_diff_mean = ''  # S&P500 데이터가 없으면 빈 값으로 설정

        # 주식 정보 업데이트
        info = obj[ticker].info
        stats[ticker].update({
            'marketCap': round(info.get('marketCap', 0) / 1e9, 1) if info.get('marketCap') not in ['', None] else '',
            'beta': info.get('beta', ''),
            'beta"': beta_diff_mean,  # S&P500과의 일일 변동율 차이의 평균
            'trailingPE': info.get('trailingPE', ''),
            'forwardPE': info.get('forwardPE', ''),
        })
        
    return stats, sp500_change_rate.mean() * 100 if sp500_change_rate is not None else None

def save_to_excel(stats):
    df = pd.DataFrame.from_dict(stats, orient='index')
    df = df[df.columns[::-1]]  # Reverse the column order
    with pd.ExcelWriter('stats.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1')
    os.startfile("stats.xlsx")

def main():
    tickers = read_tickers('ticker.txt')  # 티커 파일 경로
    prices = get_stock_data(tickers)
    obj = yf.Tickers(tickers).tickers
    
    try:
        stats, basis_change_rate = calculate_stats(prices, obj, tickers)
        save_to_excel(stats)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()