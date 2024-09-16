import requests
import json

# 전고점
hist_top_btc = 97364032
hist_top_eth = 5778651

# 잔고
btc_amt = 0.38324480
eth_amt = 0

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
krw_eth = get_ticker_price('krw-eth')

# print(krw_btc.keys())

btc_cur_price = krw_btc['trade_price']
eth_cur_price = krw_eth['trade_price']

print('-----------------------------------')
print('BTC 현재가 :', btc_cur_price)
print('ETH 현재가 :', eth_cur_price)
print('-----------------------------------')
print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('ETH 전고점대비 : {}%'.format(round((eth_cur_price-hist_top_eth)/hist_top_eth*100, 2)))
print('-----------------------------------')
print('BTC 일일 변동 :', round(krw_btc['signed_change_rate'] * 100, 2), '%')
print('ETH 일일 변동 :', round(krw_eth['signed_change_rate'] * 100, 2), '%')
print('-----------------------------------')
print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000), "만원 /", round(btc_amt, 3), 'BTC')
print('ETH 잔고 :', round((krw_eth['trade_price'] * eth_amt)/10000), "만원 /", round(eth_amt, 3), 'ETH')
print('-----------------------------------')
print('TOTAL ACCOUNT :', round((krw_btc['trade_price'] * btc_amt + krw_eth['trade_price'] * eth_amt)/10000, 1))