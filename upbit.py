import requests
import json

# 전고점
hist_top_btc = 152558528
hist_top_doge = 666

# 잔고
btc_amt = 0.40087402
doge_amt = 0

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
krw_doge = get_ticker_price('krw-doge')

# print(krw_btc.keys())

btc_cur_price = krw_btc['trade_price']
doge_cur_price = krw_doge['trade_price']

print('-----------------------------------')
print('BTC 현재가 :', btc_cur_price)
print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('BTC 일일 변동 :', round(krw_btc['signed_change_rate'] * 100, 2), '%')
print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000), "만원 /", round(btc_amt, 3), 'BTC')
print('-----------------------------------')
print('DOGE 현재가 :', doge_cur_price)
print('DOGE 전고점대비 : {}%'.format(round((doge_cur_price-hist_top_doge)/hist_top_doge*100, 2)))
print('DOGE 일일 변동 :', round(krw_btc['signed_change_rate'] * 100, 2), '%')
print('DOGE 잔고 :', round((krw_doge['trade_price'] * doge_amt)/10000), "만원 /", round(doge_amt, 3), 'DOGE')
print('-----------------------------------')
print('TOTAL ACCOUNT :', round((krw_btc['trade_price'] * btc_amt + krw_doge['trade_price'] * doge_amt)/10000, 1))