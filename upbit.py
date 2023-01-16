import requests
import json

hist_top_btc = 81100000
hist_top_eth = 5780000

avg_hold_btc = 46620107
avg_hold_eth = 1895350

last_btc_order = 21994000
last_eth_order = 1576000

btc_amt = 0.15439271
eth_amt = 2.62 + 0.33022699

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
krw_eth = get_ticker_price('krw-eth')

btc_cur_price = krw_btc['trade_price']
eth_cur_price = krw_eth['trade_price']

print('KRW-BTC : {}, 구매대비 : {}%, 어제대비 : {}%'.format(btc_cur_price, round((btc_cur_price-last_btc_order)/last_btc_order*100, 2), round(krw_btc['signed_change_rate'] * 100, 2)))
print('KRW-ETH : {}, 구매대비 : {}%, 어제대비 : {}%'.format(eth_cur_price, round((eth_cur_price-last_eth_order)/last_eth_order*100, 2), round(krw_eth['signed_change_rate'] * 100, 2)))

print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('ETH 전고점대비 : {}%'.format(round((eth_cur_price-hist_top_eth)/hist_top_eth*100, 2)))

print('BTC 수익률 : {}%'.format(round((btc_cur_price-avg_hold_btc)/avg_hold_btc*100, 2)))
print('ETH 수익률 : {}%'.format(round((eth_cur_price-avg_hold_eth)/avg_hold_eth*100, 2)))

print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000, 2))
print('ETH 잔고 :', round((krw_eth['trade_price'] * eth_amt)/10000, 2))

print('TOTAL ACCOUNT :', round((krw_btc['trade_price'] * btc_amt + krw_eth['trade_price'] * eth_amt)/10000, 2))