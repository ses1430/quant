import os
import argparse
import warnings
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
import ta

warnings.simplefilter(action="ignore", category=FutureWarning)

# ── 상수 ──────────────────────────────────────────────────────────────────────
RSI_WINDOW = 14
BB_WINDOW = 14
BB_DEV = 2
OUTPUT_FILE = "price.xlsx"

# ── 주식 분할 수동 보정 ────────────────────────────────────────────────────────
# 형식: "TICKER/YYYYMMDD/1:RATIO"  (해당 일자 이전 주가를 RATIO로 나눔)
# 예시: "1629.T/20260331/1:500"  → 1629.T의 2026-03-31 이전 주가 ÷ 500
# 데이터가 정상화되면 해당 줄만 제거하면 됨
SPLIT_ADJUSTMENTS: list[str] = [
    "1629.T/20260329/1:500",
]


# ── 유틸 ──────────────────────────────────────────────────────────────────────
def load_tickers(path: str = "ticker.txt") -> list[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=int, default=16, help="과거 데이터 기간 (기본값: 16년)")
    return parser.parse_args()


# ── 데이터 로딩 ───────────────────────────────────────────────────────────────
def download_close(tickers: list[str], years: int) -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=years * 365 + 5)
    raw = yf.download(tickers, start=start, end=end, rounding=True, ignore_tz=True)
    close = raw["Close"].copy()
    close.index = close.index.tz_localize(None)
    return close


def apply_split_adjustments(df: pd.DataFrame, adjustments: list[str]) -> pd.DataFrame:
    """SPLIT_ADJUSTMENTS 목록을 파싱해 해당 종목/일자 이전 주가를 보정한다."""
    df = df.copy()
    for entry in adjustments:
        ticker, date_str, ratio_str = entry.split("/")
        cutoff = pd.Timestamp(date_str)
        denominator = int(ratio_str.split(":")[1])
        if ticker in df.columns:
            mask = df.index <= cutoff
            df.loc[mask, ticker] = df.loc[mask, ticker] / denominator
    return df


def fill_calendar_days(df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """거래일 사이의 비거래일을 전일 종가로 채운 일별 DataFrame 반환."""
    full_index = pd.date_range(df.index[0], df.index[-1], freq="D")
    return df.reindex(full_index).ffill()[tickers]


# ── 지표 계산 ─────────────────────────────────────────────────────────────────
def _resample(series: pd.Series) -> dict[str, pd.Series]:
    return {
        "D": series,
        "W": series.resample("W-FRI").last(),
        "M": series.resample("ME").last(),
    }


def compute_indicators(series: pd.Series) -> dict[str, float]:
    frames = _resample(series)
    result: dict[str, float] = {}

    for label, s in frames.items():
        result[f"RSI.{label}"] = ta.momentum.rsi(s, window=RSI_WINDOW).iloc[-1]
        result[f"BB.{label}"] = (
            ta.volatility.bollinger_pband(s, BB_WINDOW, BB_DEV, fillna=True).iloc[-1] * 100
        )

    order = ["RSI.D", "RSI.W", "RSI.M", "BB.D", "BB.W", "BB.M"]
    return {k: result[k] for k in order}


def build_stat(close: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    records = {ticker: compute_indicators(close[ticker]) for ticker in tickers}
    return pd.DataFrame(records, dtype="float64").iloc[::-1]


# ── 엑셀 출력 ─────────────────────────────────────────────────────────────────
def export_excel(df_filled: pd.DataFrame, df_stat: pd.DataFrame, path: str) -> None:
    combined = pd.concat([df_filled, df_stat]).iloc[::-1].T
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        combined.to_excel(writer, sheet_name="Sheet1")


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main() -> None:
    args = parse_args()
    tickers = load_tickers()

    print(f"[1/4] {len(tickers)}개 종목 다운로드 중 ({args.years}년)...")
    close = download_close(tickers, args.years)
    close = apply_split_adjustments(close, SPLIT_ADJUSTMENTS)

    print("[2/4] 캘린더 일별 데이터 생성 중...")
    df_filled = fill_calendar_days(close, tickers)

    print("[3/4] RSI / 볼린저밴드 지표 계산 중...")
    df_stat = build_stat(close, tickers)

    print(f"[4/4] 엑셀 저장 → {OUTPUT_FILE}")
    export_excel(df_filled, df_stat, OUTPUT_FILE)

    os.startfile(OUTPUT_FILE)


if __name__ == "__main__":
    main()