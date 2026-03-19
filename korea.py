import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import ta
from datetime import datetime, timedelta
import os
from typing import Dict


# ==================== 설정 ====================
TICKER_FILE = 'kor_ticker.dat'
OUTPUT_FILE = 'kdrx.xlsx'

YEARS_BACK = 5
VOL_WINDOW_DAYS = 180
RSI_WINDOW = 14
BB_WINDOW = 14
BB_DEV = 2.0

REFERENCE_TICKER_CODE = '379800'          # KODEX S&P500 (정규화 기준)
# ============================================


def load_ticker_dict(file_path: str) -> Dict[str, str]:
    """kor_ticker.dat 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return {
            line.split('\t')[0]: line.split('\t')[1].strip()
            for line in f.readlines() if line.strip()
        }


def download_close_data(ticker_dict: Dict[str, str], years_back: int = 5) -> pd.DataFrame:
    """종가 데이터 일괄 다운로드"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365 * years_back + 30)
    
    print(f"📥 종가 데이터 다운로드 중 ({len(ticker_dict)}개 종목)...")
    
    data_list = []
    for code, name in ticker_dict.items():
        try:
            df = fdr.DataReader(code, start_date, end_date)[['Close']]
            df.columns = [name]
            data_list.append(df)
        except Exception:
            print(f"   ⚠️ 실패: {code} ({name})")
    
    data = pd.concat(data_list, axis=1)
    print(f"✅ 종가 다운로드 완료: {data.shape[1]}개 종목")
    return data


def fill_calendar_days(data: pd.DataFrame) -> pd.DataFrame:
    """주말/공휴일 포함 전체 날짜 채우기"""
    full_index = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
    return data.reindex(full_index).ffill()


def calculate_historical_volatility(prices: pd.Series, window: int = 180) -> float:
    """연율화 Historical Volatility"""
    log_ret = np.log(prices / prices.shift(1)).dropna()
    daily_vol = log_ret.rolling(window=min(window, len(log_ret))).std().iloc[-1]
    return daily_vol * np.sqrt(252) * 100


def calculate_indicators(data: pd.DataFrame, ticker_dict: Dict[str, str]) -> pd.DataFrame:
    """RSI / BB / HV 계산"""
    stats = {}
    for code, name in ticker_dict.items():
        if name not in data.columns: continue
        series = data[name].dropna()
        if len(series) < 30: continue
            
        weekly = series.resample('W-FRI').last()
        monthly = series.resample('ME').last()
        
        stats[name] = {
            'HV.180': calculate_historical_volatility(series, VOL_WINDOW_DAYS),
            'RSI.일': ta.momentum.rsi(series, window=RSI_WINDOW).iloc[-1],
            'RSI.주': ta.momentum.rsi(weekly, window=RSI_WINDOW).iloc[-1],
            'RSI.월': ta.momentum.rsi(monthly, window=RSI_WINDOW).iloc[-1],
            'BB.일': ta.volatility.bollinger_pband(series, window=BB_WINDOW, window_dev=BB_DEV).iloc[-1] * 100,
            'BB.주': ta.volatility.bollinger_pband(weekly, window=BB_WINDOW, window_dev=BB_DEV).iloc[-1] * 100,
            'BB.월': ta.volatility.bollinger_pband(monthly, window=BB_WINDOW, window_dev=BB_DEV).iloc[-1] * 100,
        }
    
    return pd.DataFrame(stats)



def normalize_volatility(stat_df: pd.DataFrame, ref_name: str) -> pd.DataFrame:
    """KODEX S&P500 기준 HV.180 정규화"""
    if ref_name in stat_df.columns:
        stat_df.loc['HV.180'] = stat_df.loc['HV.180'] / stat_df.loc['HV.180', ref_name]
        print(f"✅ HV.180 정규화 완료 (기준: {ref_name})")
    return stat_df


def main():
    ticker_dict = load_ticker_dict(TICKER_FILE)
    ref_name = ticker_dict.get(REFERENCE_TICKER_CODE, "KODEX S&P500")
    
    # 1. 데이터 다운로드 & 캘린더 채우기
    price_df = download_close_data(ticker_dict, YEARS_BACK)
    price_df = fill_calendar_days(price_df)
    
    # 2. 기술적 지표 계산
    stat_df = calculate_indicators(price_df, ticker_dict)
    
    # 3. Volatility 정규화
    stat_df = normalize_volatility(stat_df, ref_name)
    
    # ==================== 핵심 수정 ====================
    # 가격 컬럼을 최근 날짜 → 과거 날짜 순으로 정렬 (엑셀 보기 편하게)
    price_sorted = price_df.sort_index(ascending=False)

    # 지표 먼저 + 최근→과거 가격 순으로 concat → .T
    combined = pd.concat([stat_df, price_sorted], axis=0)

    # kor_ticker.dat 파일 순서대로 열(종목) 정렬
    ordered_names = [name for name in ticker_dict.values() if name in combined.columns]
    combined = combined[ordered_names]

    result = combined.T
    # ==================================================
    
    # 저장 및 자동 열기
    result.to_excel(OUTPUT_FILE, sheet_name='All')
    print(f"\n💾 저장 완료 → {OUTPUT_FILE} (열 순서 정상화됨)")
    
    if os.name == 'nt':
        os.startfile(OUTPUT_FILE)


if __name__ == "__main__":
    main()