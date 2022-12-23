import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt
import subprocess
import ta
import os

stocks = {item.split('\t')[0]:item.split('\t')[1] for item in open('kor_ticker.dat', 'r', encoding='utf-8').readlines()}

start_dt = (dt.datetime.now() - dt.timedelta(days=1850)).strftime('%Y-%m-%d')
end_dt = dt.datetime.now().strftime('%Y-%m-%d')

df_list = [fdr.DataReader(t, start_dt, end_dt)['Close'] for t in stocks]
df = pd.concat(df_list, axis=1)
df.columns = list(stocks.values())
#df = data.replace({np.nan: None})

rsi = {}
for column in df.columns:
    rsi[column] = ta.momentum.rsi(df[column])[-1]

df = pd.concat([df, pd.DataFrame(data=[rsi])]).iloc[::-1].T
df.rename(columns={df.columns[0]:'RSI'}, inplace=True)

writer = pd.ExcelWriter('kdrx.xlsx', engine='xlsxwriter')

#최근 120일치만 가져오기
df.to_excel(writer, sheet_name='Sheet1')
writer.close()

# subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE kdrx.xlsx")
# subprocess.call("C:\\Program Files\\Microsoft Office 15\\root\\office15\\EXCEL.EXE kdrx.xlsx")
os.startfile("kdrx.xlsx")