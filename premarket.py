import yfinance as yf
import pandas as pd
import os

# 티커 목록이 포함된 파일 읽기 (예: tickers.txt)
def read_tickers(file_path):
    with open(file_path, 'r') as file:
        tickers = [line.strip() for line in file if line.strip()]
    return tickers

# 가장 최근 가격 가져오기
def get_latest_prices(tickers):
    latest_data = {'Ticker': [], 'Latest Price': []}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            
            # 최근 2일 데이터 가져오기 (프리장/장후 포함)
            hist = stock.history(period="2d", prepost=True, interval="1m")
            
            latest_data['Ticker'].append(ticker)
            if not hist.empty:
                # 가장 최근 종가 가져오기
                latest_price = hist['Close'].iloc[-1]
                latest_data['Latest Price'].append(latest_price)
            elif len(hist) > 1:
                # 데이터가 없으면 전일 종가 가져오기
                previous_close = hist['Close'].iloc[-2]  # 전일 종가
                latest_data['Latest Price'].append(previous_close)
            else:
                latest_data['Latest Price'].append("데이터 없음")
                
        except Exception as e:
            latest_data['Ticker'].append(ticker)
            latest_data['Latest Price'].append(f"에러: {str(e)}")
    
    return latest_data

# 메인 실행
if __name__ == "__main__":
    # 티커 파일 경로 (사용자 환경에 맞게 수정 필요)
    file_path = "ticker.txt"
    
    # 티커 읽기
    tickers = read_tickers(file_path)
    
    # 가장 최근 가격 가져오기
    data = get_latest_prices(tickers)
    
    # 데이터프레임으로 변환
    df = pd.DataFrame(data)
    
    # 엑셀 파일로 저장
    output_file = "premarket.xlsx"
    df.to_excel(output_file, index=False)

    # 엑셀 파일 열기
    os.startfile("premarket.xlsx")