import yfinance as yf
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import OrderedDict
import warnings
import sys

warnings.simplefilter(action='ignore', category=FutureWarning)

# 환율 캐싱을 위한 전역 딕셔너리
exchange_rates = {}

def read_tickers(filename='ticker.txt'):
    """
    'ticker.txt' 파일에서 티커 목록을 읽어옵니다.
    #으로 시작하는 줄은 주석으로 간주하여 제외합니다.
    """
    with open(filename, 'r') as file:
        return [t.strip() for t in file if not t.startswith('#')]

def get_stock_data(tickers):
    """
    지정된 티커 목록에 대해 최근 6개월간의 주식 데이터를 다운로드합니다.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 최근 6개월 데이터
    # yfinance.download는 여러 티커의 데이터를 멀티인덱스 DataFrame으로 반환합니다.
    return yf.download(tickers, start=start_date, end=end_date, interval='1d', rounding=True, ignore_tz=True)

def get_exchange_rate(currency):
    """
    해당 통화의 달러 환율을 가져오는 함수입니다.
    가져온 환율은 캐싱하여 불필요한 API 호출을 줄입니다.
    """
    if currency == 'USD':
        return 1.0
    if currency in exchange_rates:
        return exchange_rates[currency]  # 캐싱된 환율 반환

    ticker = f"{currency}USD=X"  # 예: JPYUSD=X는 엔화-달러 환율
    data = yf.download(ticker, period='1d')
    if not data.empty and ticker in data['Close'].columns: # 데이터가 있고 해당 티커 컬럼이 있는지 확인
        exchange_rate = data['Close'][ticker].iloc[-1]
        exchange_rates[currency] = exchange_rate  # 딕셔너리에 저장
        return exchange_rate
    else:
        raise ValueError(f"환율 데이터를 가져오지 못했습니다: {currency}")

def calculate_stats(prices, obj, tickers):
    """
    각 티커에 대한 통계 지표(PE, Beta, 변동성 지표, 시가총액)를 계산합니다.
    """
    stats = OrderedDict()
    sp500_change_rate = None  # S&P500 지수의 일일 변동율 저장용
    sp500_historical_volatility = None # S&P500 지수의 역사적 변동성 저장용

    # S&P500 지수의 일일 변동율 및 역사적 변동성 계산
    if '^GSPC' in prices['Close'].columns:
        sp500_prices = prices['Close']['^GSPC']
        sp500_change_rate = sp500_prices.pct_change()  # S&P500 일일 변동율
        if not sp500_change_rate.empty:
            sp500_historical_volatility = sp500_change_rate.std() * (252**0.5) * 100

    # 각 티커에 대해 통계 계산
    for ticker in tickers:
        stats[ticker] = OrderedDict({
            'marketCap': '',
            'beta': '',
            'beta"': '', # S&P500 역사적 변동성 대비
            'trailingPE': '',
            'forwardPE': '',            
        })

        # 해당 티커의 데이터가 없는 경우 경고 메시지 출력 후 다음 티커로 이동
        if ticker not in prices['Close'].columns:
            print(f"경고: {ticker}에 대한 데이터를 찾을 수 없습니다.")
            continue

        # 주식의 일일 변동율 계산 (Historical Volatility 계산에 사용)
        stock_close_prices = prices['Close'][ticker]
        stock_change_rate = stock_close_prices.pct_change()  # 주식 일일 변동율

        # 1. 역사적 변동성 (Historical Volatility, HV) 계산 (계산은 유지하되, 결과에 포함하지 않음)
        historical_volatility = ''
        if not stock_change_rate.empty:
            historical_volatility = stock_change_rate.std() * (252**0.5) * 100
        
        # historicalVolatility를 S&P500 historicalVolatility로 나눈 값 계산
        relative_historical_vol_vs_sp500 = ''
        if historical_volatility != '' and sp500_historical_volatility is not None and sp500_historical_volatility != 0:
            relative_historical_vol_vs_sp500 = historical_volatility / sp500_historical_volatility

        # yfinance info 객체에서 기본 정보 가져오기
        info = obj[ticker].info
        currency = info.get('currency', 'USD')  # 통화 확인
        market_cap = info.get('marketCap', 0)   # 시가총액 가져오기

        # 시가총액을 달러로 변환 (필요시)
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
            stats[ticker]['marketCap'] = round(market_cap_usd / 1e9, 1)  # 억 달러 단위로 표시
        else:
            stats[ticker]['marketCap'] = ''

        # 최종 통계 딕셔너리 업데이트
        stats[ticker].update({
            'beta': info.get('beta', ''), # yfinance에서 제공하는 베타값
            'beta"': relative_historical_vol_vs_sp500,
            'trailingPE': info.get('trailingPE', ''),
            'forwardPE': info.get('forwardPE', ''),
        })
    return stats, sp500_change_rate.mean() * 100 if sp500_change_rate is not None else None

def save_to_excel(stats):
    """
    계산된 통계 데이터를 'stats.xlsx' 파일로 저장하고 엽니다.
    열 순서를 재정렬하여 가독성을 높입니다.
    """
    df = pd.DataFrame.from_dict(stats, orient='index')
    
    # 원하는 열 순서 정의 (PE, Beta, 변동성 지표들, MarketCap)
    desired_columns_order = [
        'marketCap', 
        'beta',
        'beta"',
        #'trailingPE',
        #'forwardPE',
    ]
    
    # 실제 데이터프레임에 있는 컬럼만 필터링하여 순서 적용
    # intersection을 사용하여 실제 데이터에 없는 컬럼이 있어도 오류가 발생하지 않도록 합니다.
    df = df[df.columns.intersection(desired_columns_order)]

    with pd.ExcelWriter('stats.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1')
    
    # 생성된 엑셀 파일 열기 (Windows 환경 가정)
    try:
        os.startfile("stats.xlsx")
    except AttributeError:
        print("엑셀 파일을 자동으로 열 수 없습니다. 'stats.xlsx' 파일을 수동으로 열어주세요.")
    except Exception as e:
        print(f"엑셀 파일 열기 중 오류 발생: {e}")

def main():
    """
    메인 함수: 티커 읽기, 데이터 가져오기, 통계 계산, 엑셀 저장 및 열기 과정을 수행합니다.
    커맨드 라인 인자로 파일명을 받아 처리합니다.
    """
    # len(sys.argv)는 커맨드 라인 인자의 개수+1(스크립트 파일명 자체) 입니다.
    # 인자가 주어지면(>1) 그 값을 파일명으로 사용하고, 없으면 기본값을 사용합니다.
    if len(sys.argv) > 1:
        ticker_filename = sys.argv[1]
    else:
        ticker_filename = 'ticker.txt'  # 기본 파일명

    print(f"'{ticker_filename}' 파일에서 티커 목록을 읽어옵니다.")

    try:
        tickers = read_tickers(ticker_filename)  # 파일명을 인자로 전달
    except FileNotFoundError:
        print(f"오류: '{ticker_filename}' 파일을 찾을 수 없습니다. 프로그램을 종료합니다.")
        return  # 파일이 없으면 프로그램 종료
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # S&P500 지수 티커 추가 (시장 대비 변동성 계산을 위해)
    if '^GSPC' not in tickers:
        tickers.append('^GSPC') 
    
    prices = get_stock_data(tickers) # 주식 데이터 다운로드
    obj = yf.Tickers(tickers).tickers # yfinance Tickers 객체 생성 (정보 가져오기 위함)
    
    try:
        stats, basis_change_rate = calculate_stats(prices, obj, tickers)
        # ^GSPC는 통계 결과에서 제외
        if '^GSPC' in stats:
            del stats['^GSPC']
        save_to_excel(stats)
    except Exception as e:
        print(f"통계 계산 또는 엑셀 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()

    