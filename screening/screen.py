import yfinance as yf
import pandas as pd
import os
import warnings
import sys
from datetime import datetime, timedelta
import ta

warnings.simplefilter(action='ignore', category=FutureWarning)

# 명령줄 인자로 파일명 받기 (첫 번째 인자: 스크립트 이름, 두 번째 인자: 파일명)
if len(sys.argv) != 2:
    print("사용법: python screen.py <파일명>")
    print("예: python screen.py input.txt")
    exit()

file_name = sys.argv[1]

# 대상 티커 목록 읽기
try:
    stocks = open(file_name, 'r').readlines()
    stocks = [t.strip() for t in stocks if not t.startswith('#')]
    if not stocks:
        raise ValueError("파일이 비어 있거나 유효한 티커가 없습니다.")
except FileNotFoundError:
    print(f"파일 '{file_name}'을(를) 찾을 수 없습니다. 프로그램을 종료합니다.")
    exit()
except Exception as e:
    print(f"파일 읽기 중 오류가 발생했습니다: {e}")
    exit()

# 주가 데이터 다운로드 (일 단위, 최대 기간)
data = yf.download(stocks, interval='1d', period='max', rounding=True, ignore_tz=True)
df = data['Close']

# 최근 15년 데이터 필터링
start_date = df.index[-1] - timedelta(days=15*365+5)
df = df[df.index >= start_date]

# 인덱스를 timezone-naive로 변환
df.index = df.index.tz_localize(None)

# 연간 수익률 계산 (2010-2024)
annual_returns = {}
for year in range(2010, 2025):
    year_data = df[df.index.year == year]
    if not year_data.empty and len(year_data) > 1:
        annual_returns[year] = (year_data.iloc[-1] / year_data.iloc[0] - 1) * 100
    else:
        annual_returns[year] = None
annual_returns_df = pd.DataFrame(annual_returns)

# CAGR 계산 (1, 3, 5, 10년)
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

# 연간 수익률과 CAGR 결합
performance_df = pd.concat([annual_returns_df, cagr_df], axis=1)
performance_df.columns = [str(y) for y in range(2010, 2025)] + ['1y', '3y', '5y', '10y']

# 새로운 추출항목을 위한 데이터프레임 초기화
additional_data = pd.DataFrame(index=stocks)

# RSI와 Bollinger Band 계산
for ticker in stocks:
    # 일 단위 RSI와 Bollinger Band
    rsi_day = ta.momentum.rsi(df[ticker], window=14).iloc[-1]
    bb_pband_day = ta.volatility.bollinger_pband(df[ticker], window=14).iloc[-1]
    
    # 주 단위 데이터 생성 및 RSI, Bollinger Band 계산
    df_week = df[ticker].resample('W').last()
    rsi_week = ta.momentum.rsi(df_week, window=14).iloc[-1] if len(df_week) >= 14 else None
    bb_pband_week = ta.volatility.bollinger_pband(df_week, window=14).iloc[-1] if len(df_week) >= 14 else None
    
    # 월 단위 데이터 생성 및 RSI, Bollinger Band 계산
    df_month = df[ticker].resample('M').last()
    rsi_month = ta.momentum.rsi(df_month, window=14).iloc[-1] if len(df_month) >= 14 else None
    bb_pband_month = ta.volatility.bollinger_pband(df_month, window=14).iloc[-1] if len(df_month) >= 14 else None
    
    # 데이터프레임에 추가
    additional_data.loc[ticker, 'RSI.d'] = rsi_day    
    additional_data.loc[ticker, 'RSI.w'] = rsi_week    
    additional_data.loc[ticker, 'RSI.M'] = rsi_month

    additional_data.loc[ticker, 'BB.d'] = bb_pband_day * 100
    additional_data.loc[ticker, 'BB.w'] = bb_pband_week * 100
    additional_data.loc[ticker, 'BB.M'] = bb_pband_month * 100

# Trailing P/E, Dividend Yield, Beta 가져오기
for ticker in stocks:
    stock_info = yf.Ticker(ticker).info
    additional_data.loc[ticker, 'Name'] = stock_info.get('shortName') or stock_info.get('longName', None)
    additional_data.loc[ticker, 'marketCap'] = stock_info.get('marketCap', 0)
    additional_data.loc[ticker, 'Industry'] = stock_info.get('industry', None)
    additional_data.loc[ticker, 'P/E'] = stock_info.get('trailingPE', None)
    additional_data.loc[ticker, 'div'] = stock_info.get('dividendYield', None) if stock_info.get('dividendYield') else None
    additional_data.loc[ticker, 'beta'] = stock_info.get('beta', None)

# 기존 데이터프레임과 새로운 데이터 결합
final_df = pd.concat([performance_df, additional_data], axis=1)

# 엑셀 파일로 내보내기
output_file = 'screen.xlsx'
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    final_df.to_excel(writer, sheet_name='Performance')

# 엑셀 파일 열기
os.startfile(output_file)