import yfinance as yf
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import OrderedDict

# 환율 캐싱을 위한 전역 딕셔너리
exchange_rates = {}

def read_tickers(filename):
    with open(filename, 'r') as file:
        return [t.strip() for t in file if not t.startswith('#')]

def get_stock_data(tickers):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1년 전 데이터
    return yf.download(tickers, start=start_date, end=end_date, interval='1d', rounding=True, ignore_tz=True)

def get_exchange_rate(currency):
    """해당 통화의 달러 환율을 가져오는 함수"""
    if currency == 'USD':
        return 1.0
    
    if currency in exchange_rates:
        return exchange_rates[currency]  # 캐싱된 환율 반환

    ticker = f"{currency}USD=X"  # 예: JPYUSD=X는 엔화-달러 환율
    data = yf.download(ticker, period='1d')
    if not data.empty:
        exchange_rate = data['Close'][ticker].iloc[-1]
        exchange_rates[currency] = exchange_rate  # 딕셔너리에 저장
        
        return exchange_rate
    else:
        raise ValueError(f"환율 데이터를 가져오지 못했습니다: {currency}")

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
        currency = info.get('currency', 'USD')  # 통화 확인
        market_cap = info.get('marketCap', 0)   # 시가총액 가져오기

        if market_cap and market_cap != '':
            if currency != 'USD':
                try:                    
                    exchange_rate = get_exchange_rate(currency)  # 환율 가져오기
                    market_cap_usd = market_cap * exchange_rate  # 달러로 변환
                except Exception as e:
                    print(f"{ticker} 시가총액 변환 오류: {e}")
                    market_cap_usd = ''
            else:
                market_cap_usd = market_cap
            stats[ticker]['marketCap'] = round(market_cap_usd / 1e9, 1)  # 억 달러 단위
        else:
            stats[ticker]['marketCap'] = ''

        stats[ticker].update({
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