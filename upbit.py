import requests
import json

hist_top_btc = 175846045
btc_amt = 0.42508929

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
btc_cur_price = krw_btc['trade_price']

print('-----------------------------------')
print('BTC 현재가 :', btc_cur_price)
print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('BTC 일일 변동 :', round(krw_btc['signed_change_rate'] * 100, 2), '%')
print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000), "만원 /", round(btc_amt, 3), 'BTC')
print('TOTAL ACCOUNT :', round(krw_btc['trade_price'] * btc_amt / 10000, 1))
