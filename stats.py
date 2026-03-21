import yfinance as yf
import os
import pandas as pd
from datetime import datetime
from collections import OrderedDict
import warnings
import sys

warnings.simplefilter(action='ignore', category=FutureWarning)

exchange_rates = {}


def read_tickers(filename='ticker.txt'):
    with open(filename, 'r') as f:
        return [t.strip() for t in f if t.strip() and not t.startswith('#')]


def get_stock_data(tickers):
    return yf.download(tickers, start='2010-01-01', end=datetime.now(), interval='1d', rounding=True, ignore_tz=True)


def get_exchange_rate(currency):
    if currency == 'USD':
        return 1.0
    if currency in exchange_rates:
        return exchange_rates[currency]

    ticker = f"{currency}USD=X"
    data = yf.download(ticker, period='1d')
    if not data.empty and ticker in data['Close'].columns:
        exchange_rates[currency] = data['Close'][ticker].iloc[-1]
        return exchange_rates[currency]

    raise ValueError(f"환율 데이터를 가져오지 못했습니다: {currency}")


def _calc_market_cap(info, currency):
    if info.get('quoteType') == 'ETF':
        market_cap = info.get('totalAssets', 0)
    else:
        market_cap = info.get('marketCap', 0)

    if not market_cap:
        return ''
    if currency == 'USD':
        return round(market_cap / 1e9, 1)
    if currency == 'KRW':
        return round(market_cap / 1e8, 1)

    exchange_rate = get_exchange_rate(currency)
    return round(market_cap * exchange_rate / 1e9, 1)


def calculate_stats(prices, obj, tickers):
    stats = OrderedDict()
    sp500_change_rate = None
    sp500_historical_volatility = None

    if '^GSPC' in prices['Close'].columns:
        sp500_change_rate = prices['Close']['^GSPC'].pct_change()
        if not sp500_change_rate.empty:
            sp500_historical_volatility = sp500_change_rate.std() * (252**0.5) * 100

    for ticker in tickers:
        stats[ticker] = OrderedDict({
            'marketCap': '',
            'beta': '',
            'beta"': '',
            'trailingPE': '',
            'forwardPE': '',
        })

        if ticker not in prices['Close'].columns:
            print(f"경고: {ticker}에 대한 데이터를 찾을 수 없습니다.")
            continue

        stock_close_prices = prices['Close'][ticker]
        stock_change_rate = stock_close_prices.pct_change()

        historical_volatility = None
        if not stock_change_rate.empty:
            historical_volatility = stock_change_rate.std() * (252**0.5) * 100

        relative_historical_vol_vs_sp500 = ''
        if historical_volatility is not None and sp500_historical_volatility:
            relative_historical_vol_vs_sp500 = historical_volatility / sp500_historical_volatility

        info = obj[ticker].info
        currency = info.get('currency', 'USD')

        try:
            market_cap_val = _calc_market_cap(info, currency)
        except Exception as e:
            print(f"{ticker} 시가총액 변환 오류: {e}")
            market_cap_val = ''

        stats[ticker].update({
            'marketCap': market_cap_val,
            'beta': info.get('beta', ''),
            'beta"': relative_historical_vol_vs_sp500,
            'trailingPE': info.get('trailingPE', ''),
            'forwardPE': info.get('forwardPE', ''),
        })

        yearly_prices = stock_close_prices.resample('Y').last().dropna()
        for year in range(2011, 2026):
            prev = yearly_prices.loc[f'{year-1}-12-31':f'{year-1}-12-31'].values
            curr = yearly_prices.loc[f'{year}-12-31':f'{year}-12-31'].values
            if len(prev) > 0 and len(curr) > 0 and prev[0] != 0:
                stats[ticker][str(year)] = round(((curr[0] - prev[0]) / prev[0]) * 100, 2)
            else:
                stats[ticker][str(year)] = ''

    sp500_mean = sp500_change_rate.mean() * 100 if sp500_change_rate is not None else None
    return stats, sp500_mean


def save_to_excel(stats):
    df = pd.DataFrame.from_dict(stats, orient='index')

    desired_columns_order = [
        'marketCap',
        'beta',
        'beta"',
        'trailingPE',
        'forwardPE',
    ] + [str(year) for year in range(2011, 2026)]

    existing = set(df.columns)
    df = df[[c for c in desired_columns_order if c in existing]]

    with pd.ExcelWriter('stats.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1')

    try:
        os.startfile("stats.xlsx")
    except AttributeError:
        print("엑셀 파일을 자동으로 열 수 없습니다. 'stats.xlsx' 파일을 수동으로 열어주세요.")
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

    if '^GSPC' not in tickers:
        tickers.append('^GSPC')

    prices = get_stock_data(tickers)
    obj = yf.Tickers(tickers).tickers

    try:
        stats, _ = calculate_stats(prices, obj, tickers)
        stats.pop('^GSPC', None)
        save_to_excel(stats)
    except Exception as e:
        print(f"통계 계산 또는 엑셀 저장 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
