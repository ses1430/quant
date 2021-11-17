import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt
import subprocess

kdrx = {
     '003410':'쌍용C&E'
    ,'305720':'K.2차전지'
    ,'305540':'T.2차전지'    
    ,'379800':'S&P500'
    ,'379810':'나스닥'
    ,'381170':'테크Top10'    
    ,'394670':'글로벌리튬'
    ,'381180':'미국필라반'
    ,'390390':'미국반도체'
    ,'371460':'차이나전기차'
    ,'396510':'차이나클린'
    ,'396520':'차이나반도체'    
    ,'400570':'유럽탄소'
    ,'228810':'미디어컨텐츠'
    ,'263750':'펄어비스'
    ,'259960':'크래프톤'
    ,'194480':'데브시스터즈'
}

start_dt = (dt.datetime.now() - dt.timedelta(days=5)).strftime('%Y-%m-%d')
end_dt = dt.datetime.now().strftime('%Y-%m-%d')

items = list(kdrx.keys())

df_list = [fdr.DataReader(t, start_dt, end_dt)['Close'] for t in items]
df = pd.concat(df_list, axis=1)
df.columns = list(kdrx.values())
df = df.replace({np.nan: None})

writer = pd.ExcelWriter('kdrx.xlsx', engine='xlsxwriter')

#최근 120일치만 가져오기
df.iloc[::-1].to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE kdrx.xlsx")