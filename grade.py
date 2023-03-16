from yahooquery import Ticker
import os
import pandas as pd

tickers = 'AAPL MSFT GOOGL TSLA IBM NVDA AMD AVGO ASML TSM COST KO PEP PG MCD SBUX NKE DIS ATVI JNJ MMM WM LMT RMS.PA MC.PA CDI.PA P911.DE'
df = Ticker(tickers).grading_history

df2 = df.loc[(df['epochGradeDate'] >= '2023-03-01') & (df['action'] != 'main') & (df['action'] != 'reit')][['epochGradeDate','firm','action','fromGrade','toGrade']]
print(df2.droplevel(axis=0,level=1).sort_values('epochGradeDate'))

'''
writer = pd.ExcelWriter('grade.xlsx', engine='xlsxwriter')
df2.to_excel(writer, sheet_name='Sheet1')
writer.close()

os.startfile("grade.xlsx")
'''