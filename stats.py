import sys
import os
import warnings
from datetime import datetime
import concurrent.futures

import pandas as pd
import yfinance as yf

# pandas의 resample('Y') 등에서 발생하는 FutureWarning 숨기기
warnings.simplefilter(action='ignore', category=FutureWarning)

# ── 주식 분할 수동 보정 ────────────────────────────────────────────────────────
# 형식: "TICKER/YYYYMMDD/1:RATIO"  (해당 일자 이전 주가를 RATIO로 나눔)
# 예시: "1629.T/20260329/1:500"  → 1629.T의 2026-03-29 이전 주가 ÷ 500
# 데이터가 정상화되면 해당 줄만 제거하면 됨
SPLIT_ADJUSTMENTS: list[str] = [
    "1629.T/20260329/1:500",
]


class MarketDataProcessor:
    """환율 데이터 캐싱 및 시가총액 변환을 담당하는 클래스"""
    def __init__(self):
        self.exchange_rates = {'USD': 1.0}
        self.current_year = datetime.now().year
        self.start_year = 2011

    def get_exchange_rate(self, currency: str) -> float:
        if currency in self.exchange_rates:
            return self.exchange_rates[currency]

        ticker = f"{currency}USD=X"
        data = yf.download(ticker, period='1d', progress=False)
        
        try:
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    rate = float(data['Close'][ticker].iloc[-1])
                else:
                    rate = float(data['Close'].iloc[-1])
                self.exchange_rates[currency] = rate
                return rate
        except BaseException:
            pass

        raise ValueError(f"환율 데이터를 가져오지 못했습니다: {currency}")

    def calc_market_cap(self, info: dict, currency: str) -> str:
        market_cap = info.get('totalAssets', 0) if info.get('quoteType') == 'ETF' else info.get('marketCap', 0)
        
        if not market_cap:
            return ''
            
        if currency == 'USD':
            return round(market_cap / 1e9, 1)
        if currency == 'KRW':
            return round(market_cap / 1e8, 1)

        exchange_rate = self.get_exchange_rate(currency)
        return round(market_cap * exchange_rate / 1e9, 1)


def read_tickers(filename: str) -> list:
    """텍스트 파일에서 티커 목록을 읽어옵니다. (주석 및 빈 줄 무시)"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def apply_split_adjustments(prices: pd.DataFrame, adjustments: list[str]) -> pd.DataFrame:
    """SPLIT_ADJUSTMENTS 목록을 파싱해 해당 종목/일자 이전 종가를 보정한다."""
    prices = prices.copy()
    close = prices['Close'].copy()
    for entry in adjustments:
        ticker, date_str, ratio_str = entry.split("/")
        cutoff = pd.Timestamp(date_str)
        denominator = int(ratio_str.split(":")[1])
        if ticker in close.columns:
            mask = close.index <= cutoff
            close.loc[mask, ticker] = close.loc[mask, ticker] / denominator
    prices['Close'] = close
    return prices


def fetch_stock_data(tickers: list) -> pd.DataFrame:
    """yfinance를 통해 과거 주가 데이터를 다운로드합니다."""
    return yf.download(tickers, start='2010-01-01', end=datetime.now(), interval='1d', rounding=True, ignore_tz=True)


def calculate_yearly_returns(stock_prices: pd.Series, start_year: int, current_year: int) -> dict:
    """전년도 말 대비 당해 연도 말의 수익률(%)을 계산합니다."""
    returns = {}
    yearly_prices = stock_prices.resample('YE').last().dropna()
    
    for year in range(start_year, current_year + 1):
        prev_date = f"{year-1}-12-31"
        curr_date = f"{year}-12-31"
        
        prev_vals = yearly_prices.loc[prev_date:prev_date].values
        curr_vals = yearly_prices.loc[curr_date:curr_date].values
        
        if len(prev_vals) > 0 and len(curr_vals) > 0 and prev_vals[0] != 0:
            returns[str(year)] = round(((curr_vals[0] - prev_vals[0]) / prev_vals[0]) * 100, 2)
        else:
            returns[str(year)] = ''
            
    return returns


def calculate_statistics(prices: pd.DataFrame, ticker_infos: dict, tickers: list) -> tuple:
    """각 티커별 통계(베타, 시총, PER 및 연도별 수익률 등)를 계산합니다."""
    processor = MarketDataProcessor()
    stats_list = []
    
    # 멀티스레딩으로 info 데이터 병렬 수집
    print("메타데이터(info)를 병렬로 수집하는 중...")
    def fetch_info(t):
        try:
            return t, ticker_infos[t].info
        except Exception:
            return t, {}

    prefetched_infos = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_info, t): t for t in tickers if t != '^GSPC'}
        for future in concurrent.futures.as_completed(futures):
            t, info_data = future.result()
            prefetched_infos[t] = info_data

    # S&P 500 기준점(변동성 계산용) 추출
    sp500_historical_volatility = None
    if '^GSPC' in prices['Close'].columns:
        sp500_change_rate = prices['Close']['^GSPC'].pct_change()
        if not sp500_change_rate.empty:
            sp500_historical_volatility = sp500_change_rate.rolling(window=min(180, len(sp500_change_rate))).std().iloc[-1] * (252**0.5) * 100

    for ticker in tickers:           
        ticker_stats = {
            'ticker': ticker,
            'marketCap': '',
            'beta': '',
            'beta"': '',
            'trailingPE': '',
            'forwardPE': ''
        }
        
        # 년도별 칼럼 사전 초기화 (나중에 Excel 출력 순서를 보장하기 위함)
        for year in range(processor.start_year, processor.current_year + 1):
            ticker_stats[str(year)] = ''

        if ticker not in prices['Close'].columns:
            print(f"경고: {ticker}에 대한 데이터를 찾을 수 없습니다.")
            stats_list.append(ticker_stats)
            continue

        stock_close_prices = prices['Close'][ticker].dropna()
        stock_change_rate = stock_close_prices.pct_change()

        # 변동성 및 상대적 변동성(beta") 계산
        if not stock_change_rate.empty:
            historical_volatility = stock_change_rate.rolling(window=min(180, len(stock_change_rate))).std().iloc[-1] * (252**0.5) * 100
            if sp500_historical_volatility:
                ticker_stats['beta"'] = historical_volatility / sp500_historical_volatility

        # yfinance Info 기반 메타데이터 추출
        info = prefetched_infos.get(ticker, {})
        currency = info.get('currency', 'USD')

        try:
            ticker_stats['marketCap'] = processor.calc_market_cap(info, currency)
        except Exception as e:
            print(f"{ticker} 시가총액 변환 오류: {e}")

        ticker_stats['beta'] = info.get('beta', '')
        ticker_stats['trailingPE'] = info.get('trailingPE', '')
        ticker_stats['forwardPE'] = info.get('forwardPE', '')

        # 연도별 수익률 처리
        yearly_returns = calculate_yearly_returns(stock_close_prices, processor.start_year, processor.current_year)
        ticker_stats.update(yearly_returns)
        
        stats_list.append(ticker_stats)

    return stats_list, processor


def save_to_excel(stats_list: list, start_year: int, current_year: int, filename: str = 'stats.xlsx'):
    """통계 결과 리스트를 DataFrame으로 변환 후 Excel에 저장하고 실행합니다."""
    df = pd.DataFrame(stats_list)
    df.set_index('ticker', inplace=True)
    
    yearly_cols = [str(year) for year in range(start_year, current_year + 1)]
    desired_columns = ['marketCap', 'beta', 'beta"', 'trailingPE', 'forwardPE'] + yearly_cols
    
    existing_cols = set(df.columns)
    ordered_cols = [c for c in desired_columns if c in existing_cols]
    df = df[ordered_cols]

    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1')

    try:
        os.startfile(filename)
    except AttributeError:
        print(f"엑셀 파일을 자동으로 열 수 없습니다. '{filename}' 파일을 수동으로 열어주세요.")
    except Exception as e:
        print(f"엑셀 파일 열기 중 오류 발생: {e}")


def main():
    ticker_filename = sys.argv[1] if len(sys.argv) > 1 else 'ticker.txt'
    print(f"'{ticker_filename}' 파일에서 티커 목록을 읽어옵니다.")

    try:
        tickers = read_tickers(ticker_filename)
    except FileNotFoundError:
        print(f"오류: '{ticker_filename}' 파일을 찾을 수 없습니다. 프로그램을 종료합니다.")
        return
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # S&P 500은 상관계수/기준을 추적하기 위해 항상 가져옵니다
    original_has_gspc = '^GSPC' in tickers
    if not original_has_gspc:
        tickers.append('^GSPC')

    print("주가 데이터 및 메타데이터를 다운로드하는 중 (잠시만 기다려주세요)...")
    prices = fetch_stock_data(tickers)
    prices = apply_split_adjustments(prices, SPLIT_ADJUSTMENTS)
    ticker_objs = yf.Tickers(tickers).tickers

    try:
        stats_list, processor = calculate_statistics(prices, ticker_objs, tickers)
        save_to_excel(stats_list, processor.start_year, processor.current_year)
    except Exception as e:
        print(f"통계 계산 또는 엑셀 저장 중 오류가 발생했습니다: {e}")
        
if __name__ == "__main__":
    main()
