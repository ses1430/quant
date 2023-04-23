from yahooquery import Ticker
import os
import pandas as pd
import argparse
from datetime import datetime, timezone
import pytz

parser = argparse.ArgumentParser()
parser.add_argument('--date', help='the epochGradeDate value to filter on')
parser.add_argument('--ticker', help='ticker to filter on')
args = parser.parse_args()

if args.date:
    filter_date = args.date
else:
    # Set filter_date to today's date in New York timezone
    ny_tz = pytz.timezone('America/New_York')
    filter_date = datetime.now(ny_tz).strftime('%Y-%m-%d')

print("filter_date : ", filter_date)

if args.ticker:
    tickers = args.ticker
else:
    tickers = 'AAPL MSFT GOOGL TSLA IBM NVDA AMD AVGO ASML TSM COST KO PEP PG MCD SBUX NKE DIS ATVI JNJ MMM WM LMT RMS.PA MC.PA CDI.PA P911.DE'
    
df = Ticker(tickers).grading_history

df2 = df.loc[(df['epochGradeDate'] >= filter_date)][['epochGradeDate','firm','action','fromGrade','toGrade']]

print(df2)
