import yfinance as yf
import pandas as pd
import os
import warnings
import sys
from datetime import datetime, timedelta
import ta

warnings.simplefilter(action='ignore', category=FutureWarning)

# <<< 함수 정의: 데이터 처리 로직을 함수로 묶음 >>>
def process_market_data(tickers, data):
    """
    주어진 티커와 데이터에 대해 모든 분석을 수행하고 최종 데이터프레임을 반환합니다.
    """
    if data.empty:
        return pd.DataFrame()

    df = data['Close']
    # 원본 티커 순서를 유지하기 위해 reindex
    df = df.reindex(columns=tickers)

    # 연간 수익률 계산
    annual_returns = {}
    for year in range(2010, datetime.now().year + 1):
        year_data = df[df.index.year == year]
        annual_returns[year] = (year_data.iloc[-1] / year_data.iloc[0] - 1) * 100 if not year_data.empty and len(year_data) > 1 else pd.Series(index=df.columns)
    annual_returns_df = pd.DataFrame(annual_returns)

    # CAGR 계산 (1, 3, 5, 10년)
    cagr_periods = [1, 3, 5, 10]
    cagr_data = {}
    latest_date = df.index[-1]
    for period in cagr_periods:
        start_date_cagr = latest_date - timedelta(days=period * 365)
        if not df.empty and df.index[0] <= start_date_cagr:
            start_data = df[df.index >= start_date_cagr]
            start_price = start_data.bfill().iloc[0]
            cagr_values = ((df.iloc[-1] / start_price) ** (1 / period) - 1) * 100
            cagr_data[f'{period}y'] = cagr_values
        else:
            cagr_data[f'{period}y'] = pd.Series(index=df.columns, dtype=float)
    cagr_df = pd.DataFrame(cagr_data)

    performance_df = pd.concat([annual_returns_df, cagr_df], axis=1)

    additional_data = pd.DataFrame(index=tickers)

    # RSI와 Bollinger Band 계산
    for ticker in tickers:
        if ticker not in df.columns or df[ticker].dropna().empty:
            continue
        rsi_day = ta.momentum.rsi(df[ticker].dropna(), window=14).iloc[-1]
        bb_pband_day = ta.volatility.bollinger_pband(df[ticker].dropna(), window=14).iloc[-1]
        df_week = df[ticker].dropna().resample('W').last()
        rsi_week = ta.momentum.rsi(df_week, window=14).iloc[-1] if len(df_week) >= 14 else None
        bb_pband_week = ta.volatility.bollinger_pband(df_week, window=14).iloc[-1] if len(df_week) >= 14 else None
        df_month = df[ticker].dropna().resample('M').last()
        rsi_month = ta.momentum.rsi(df_month, window=14).iloc[-1] if len(df_month) >= 14 else None
        bb_pband_month = ta.volatility.bollinger_pband(df_month, window=14).iloc[-1] if len(df_month) >= 14 else None
        
        additional_data.loc[ticker, 'RSI.d'] = rsi_day    
        additional_data.loc[ticker, 'RSI.w'] = rsi_week    
        additional_data.loc[ticker, 'RSI.M'] = rsi_month
        additional_data.loc[ticker, 'BB.d'] = bb_pband_day * 100
        additional_data.loc[ticker, 'BB.w'] = bb_pband_week * 100
        additional_data.loc[ticker, 'BB.M'] = bb_pband_month * 100

    # Trailing P/E, Dividend Yield, Beta 등 상세 정보 가져오기
    for ticker in tickers:
        try:
            stock_info = yf.Ticker(ticker).info
            if not stock_info or 'symbol' not in stock_info: continue
            additional_data.loc[ticker, 'Name'] = stock_info.get('shortName') or stock_info.get('longName')
            additional_data.loc[ticker, 'marketCap'] = stock_info.get('marketCap')
            additional_data.loc[ticker, 'Industry'] = stock_info.get('industry')
            additional_data.loc[ticker, 'P/E'] = stock_info.get('trailingPE')
            additional_data.loc[ticker, 'div'] = (stock_info.get('dividendYield') or 0) * 100
            additional_data.loc[ticker, 'beta'] = stock_info.get('beta')
        except Exception:
            print(f"'{ticker}' 상세 정보 조회 실패")
            
    final_df = additional_data.join(performance_df)
    return final_df

# --- 메인 코드 시작 ---

# 명령줄 인자로 파일명 받기
if len(sys.argv) != 2:
    print("사용법: python screen.py <파일명>")
    exit()

file_name = sys.argv[1]

# 대상 티커 목록 읽기
try:
    with open(file_name, 'r') as f:
        stocks = [t.strip() for t in f.readlines() if t.strip() and not t.strip().startswith('#')]
    if not stocks:
        raise ValueError("파일이 비어 있거나 유효한 티커가 없습니다.")
except FileNotFoundError:
    print(f"'{file_name}'을(를) 찾을 수 없습니다.")
    exit()

# 티커를 미국 시장과 그 외 시장으로 자동 분리
us_stocks = [ticker for ticker in stocks if '.' not in ticker]
other_stocks = [ticker for ticker in stocks if '.' in ticker]
print(f"미국 티커 {len(us_stocks)}개, 해외 티커 {len(other_stocks)}개를 발견했습니다.")

start_date = datetime(2010, 1, 1)
end_date = datetime.now()

# <<< 수정된 부분: 데이터 다운로드 및 처리 >>>
us_final_df = None
other_final_df = None

# 미국 시장 데이터 처리
if us_stocks:
    print("미국 시장 데이터 다운로드 중...")
    us_data = yf.download(us_stocks, start=start_date, end=end_date, rounding=True, ignore_tz=True)
    us_data.index = us_data.index.tz_localize(None)
    if not us_data.empty:
        print("미국 시장 데이터 처리 중...")
        us_final_df = process_market_data(us_stocks, us_data)

# 해외 시장 데이터 처리
if other_stocks:
    print("해외 시장 데이터 다운로드 중...")
    other_data = yf.download(other_stocks, start=start_date, end=end_date, rounding=True, ignore_tz=True)
    other_data.index = other_data.index.tz_localize(None)
    if not other_data.empty:
        print("해외 시장 데이터 처리 중...")
        other_final_df = process_market_data(other_stocks, other_data)

# <<< 수정된 부분: 엑셀 파일에 시트를 분리하여 저장 >>>
output_file = 'screen_by_market.xlsx'
print(f"결과를 {output_file} 파일로 저장합니다...")
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    if us_final_df is not None and not us_final_df.empty:
        us_final_df.to_excel(writer, sheet_name='US_Market')
        print("US_Market 시트 저장 완료.")
    
    if other_final_df is not None and not other_final_df.empty:
        other_final_df.to_excel(writer, sheet_name='Other_Markets')
        print("Other_Markets 시트 저장 완료.")

# 엑셀 파일 열기
if os.path.exists(output_file):
    os.startfile(output_file)
    print("완료!")
else:
    print("저장할 데이터가 없어 엑셀 파일을 생성하지 않았습니다.")