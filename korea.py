import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt
import subprocess

kdrx = {
     '005930':'삼성전자'
    ,'005935':'삼성전자우'
    ,'207940':'삼성바이오'    
    ,'035420':'NAVER'    
    ,'206560':'덱스터'
    ,'299900':'위지윅'
    ,'003410':'쌍용C&E'
    ,'055550':'신한지주'
    ,'305720':'[K]2차전지'
    ,'305540':'[T]2차전지'
    ,'394670':'[T]글로벌리튬' 
    ,'381180':'[T]미국필반'
    ,'390390':'[K]미국반도'
    ,'371460':'[T]차이나전기차'    
    ,'396510':'[T]차이나클린'    
    ,'379810':'[K]미국나스닥'
    ,'381170':'[T]미국테크'
    ,'379800':'[K]S&P500'
    ,'400570':'[K]유럽탄소'
    ,'400580':'[S]유럽탄소'
}

start_dt = (dt.datetime.now() - dt.timedelta(days=200)).strftime('%Y-%m-%d')
end_dt = dt.datetime.now().strftime('%Y-%m-%d')

items = list(kdrx.keys())

df_list = [fdr.DataReader(t, start_dt, end_dt)['Close'] for t in items]
df = pd.concat(df_list, axis=1)
df.columns = list(kdrx.values())
df = df.replace({np.nan: None})

writer = pd.ExcelWriter('kdrx.xlsx', engine='xlsxwriter')

#최근 120일치만 가져오기
df.iloc[::-1].iloc[0:120].to_excel(writer, sheet_name='Sheet1')
writer.close()
subprocess.call("C:\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE kdrx.xlsx")