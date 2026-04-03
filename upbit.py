import os
import requests
import json
import pandas as pd
import ta
from dotenv import load_dotenv

load_dotenv()

hist_top_btc = 176015280
btc_amt = float(os.getenv('BTC_AMT', 0))

def format_krw(value):
    parts = []
    eok = int(value) // 100_000_000
    remainder = int(value) % 100_000_000
    man = remainder // 10_000
    remainder = remainder % 10_000
    cheon = remainder // 1_000
    remainder = remainder % 1_000
    if eok:
        parts.append(f'{eok}억')
    if man:
        parts.append(f'{man}만')
    if cheon:
        parts.append(f'{cheon}천')
    if remainder:
        parts.append(str(remainder))
    return ' '.join(parts) + '원'

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

def get_candles(interval, market='KRW-BTC', count=50):
    url = f"https://api.upbit.com/v1/candles/{interval}?market={market}&count={count}"
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    data = json.loads(res.text)
    # 최신 -> 과거 순으로 오므로 역순 정렬
    return [c['trade_price'] for c in reversed(data)]

def calc_indicators(closes):
    s = pd.Series(closes)
    rsi = ta.momentum.RSIIndicator(s, window=14).rsi().iloc[-1]
    bb  = ta.volatility.BollingerBands(s, window=14, window_dev=2)
    bbp = bb.bollinger_pband().iloc[-1] * 100
    return round(rsi, 1), round(bbp, 1)

# 캔들 데이터 수집 및 지표 계산
rsi_day,   bb_day   = calc_indicators(get_candles('days'))
rsi_week,  bb_week  = calc_indicators(get_candles('weeks'))
rsi_month, bb_month = calc_indicators(get_candles('months'))

krw_btc = get_ticker_price('krw-btc')
btc_cur_price = krw_btc['trade_price']

print('-----------------------------------')
print('BTC 현재가 :', format_krw(btc_cur_price))
print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('BTC 일일 변동 :', round(krw_btc['signed_change_rate'] * 100, 2), '%')
print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000), "만원 /", round(btc_amt, 5), 'BTC')
print('TOTAL ACCOUNT :', round(krw_btc['trade_price'] * btc_amt / 10000, 1))
print('-----------------------------------')
print(f'RSI(14)   일:{round(rsi_day,1):5}  주:{round(rsi_week,1):5}  월:{round(rsi_month,1):5}')
print(f'BB%B(14,2) 일:{round(bb_day,1):5}  주:{round(bb_week,1):5}  월:{round(bb_month,1):5}')
