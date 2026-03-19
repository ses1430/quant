import os
import warnings

import pandas as pd
import yfinance as yf

warnings.simplefilter(action="ignore", category=FutureWarning)

# ── 상수 ──────────────────────────────────────────────────────────────────────
TICKER_FILE = "ticker.txt"
OUTPUT_FILE = "premarket.xlsx"
PERIOD = "2d"
INTERVAL = "1m"


# ── 유틸 ──────────────────────────────────────────────────────────────────────
def load_tickers(path: str = TICKER_FILE) -> list[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# ── 데이터 로딩 ───────────────────────────────────────────────────────────────
def fetch_latest_price(ticker: str) -> float | str:
    """단일 티커의 프리/애프터마켓 포함 최근 가격 반환."""
    hist = yf.Ticker(ticker).history(period=PERIOD, prepost=True, interval=INTERVAL)
    if not hist.empty:
        return hist["Close"].iloc[-1]
    return "데이터 없음"


def build_price_table(tickers: list[str]) -> pd.DataFrame:
    records = []
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i}/{len(tickers)}] {ticker}")
        try:
            price = fetch_latest_price(ticker)
        except Exception as e:
            price = f"에러: {e}"
        records.append({"Ticker": ticker, "Latest Price": price})
    return pd.DataFrame(records)


# ── 엑셀 출력 ─────────────────────────────────────────────────────────────────
def export_excel(df: pd.DataFrame, path: str) -> None:
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main() -> None:
    tickers = load_tickers()
    print(f"[1/2] {len(tickers)}개 종목 가격 수집 중 (프리/애프터마켓 포함)...")
    df = build_price_table(tickers)

    print(f"[2/2] 엑셀 저장 → {OUTPUT_FILE}")
    export_excel(df, OUTPUT_FILE)
    os.startfile(OUTPUT_FILE)


if __name__ == "__main__":
    main()
