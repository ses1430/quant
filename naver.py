import requests
import json

def get_naver_valuation(ticker):
    """
    네이버 금융에서 PER, PBR 등 가져오기 (추정 PER 포함)
    """
    url = f"https://stock.naver.com/api/domestic/detail/{ticker}/detail?codeType=KRX"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    
    # PER, PBR이 있는 테이블 파싱
    return json.loads(res.text)

# 사용 예
print(get_naver_valuation("042660"))
print('---------------------------')
print(get_naver_valuation("475080"))
