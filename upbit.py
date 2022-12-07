import requests
import json

last_btc_order = 22711000
last_eth_order = 1593000

btc_amt = 0.14984602
eth_amt = 2.88161217

def get_ticker_price(ticker):
    url = "https://api.upbit.com/v1/ticker?markets=" + ticker
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    return json.loads(res.text)[0]

krw_btc = get_ticker_price('krw-btc')
krw_eth = get_ticker_price('krw-eth')

btc_cur_price = krw_btc['trade_price']
eth_cur_price = krw_eth['trade_price']

print('KRW-BTC : {}, 구매대비 : {}%, 어제대비 : {}%'.format(btc_cur_price, round((btc_cur_price-last_btc_order)/last_btc_order*100, 1), round(krw_btc['signed_change_rate'] * 100, 1)))
print('KRW-ETH : {}, 구매대비 : {}%, 어제대비 : {}%'.format(eth_cur_price, round((eth_cur_price-last_eth_order)/last_eth_order*100, 1), round(krw_eth['signed_change_rate'] * 100, 1)))

print('TOTAL ACCOUNT :', round((krw_btc['trade_price'] * btc_amt + krw_eth['trade_price'] * eth_amt)/10000, 1))