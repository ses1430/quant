import requests
import json

hist_top_btc = 81100000
hist_top_eth = 5780000

btc_amt = 0.15817614
eth_amt = 2.62 + 0.38308090

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
krw_eth = get_ticker_price('krw-eth')

btc_cur_price = krw_btc['trade_price']
eth_cur_price = krw_eth['trade_price']

print('BTC 전고점대비 : {}%'.format(round((btc_cur_price-hist_top_btc)/hist_top_btc*100, 2)))
print('ETH 전고점대비 : {}%'.format(round((eth_cur_price-hist_top_eth)/hist_top_eth*100, 2)))

print('BTC 잔고 :', round((krw_btc['trade_price'] * btc_amt)/10000, 2))
print('ETH 잔고 :', round((krw_eth['trade_price'] * eth_amt)/10000, 2))

print('TOTAL ACCOUNT :', round((krw_btc['trade_price'] * btc_amt + krw_eth['trade_price'] * eth_amt)/10000, 2))