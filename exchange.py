import requests
import xml.etree.ElementTree as elemTree
import sys
from datetime import datetime

currencies = ['USD','EUR','JPY']
results = []

if len(sys.argv) < 2:
    op_date = datetime.now().strftime('%Y-%m-%d')
else:
    op_date = sys.argv[1]

print('op_date :', op_date)

for cur in currencies:
    url = 'http://www.smbs.biz/ExRate/StdExRate_xml.jsp?arr_value={}_{}_{}'.format(cur, op_date, op_date)
    tree = elemTree.fromstring(requests.get(url).text.strip())

    try:
        results.append(tree.find('set').get('value'))
    except AttributeError:
        results.append('n/a')

print(' '.join(results))