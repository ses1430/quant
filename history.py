import yfinance as yf
from datetime import datetime
import argparse

def get_average_close(ticker, start_date, end_date):
    # 티커로 주식 객체 생성
    stock = yf.Ticker(ticker)
    
    # 시작일부터 현재까지의 주식 데이터 다운로드
    data = stock.history(start=start_date, end=end_date)
    # print(data)
    
    # 종가 평균 계산
    average_close = data['Close'].mean()
    
    return average_close

def main():
    # 인자 파서 설정
    parser = argparse.ArgumentParser(description="주식 티커의 평균 종가 계산")
    parser.add_argument("ticker", type=str, help="주식 티커 심볼")
    args = parser.parse_args()

    # 시작 날짜 설정
    start_date = "2024-05-12"
    end_date = "2024-09-12"

    # 평균 종가 계산
    average_close = get_average_close(args.ticker, start_date, end_date)
    
    print(f"{args.ticker}의 {start_date} ~ {end_date} 평균 종가: ${average_close:.2f}")

if __name__ == "__main__":
    main()