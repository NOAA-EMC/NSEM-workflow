import os, sys
import numpy as np
import pandas as pd

NSEMdir = os.environ['NSEMdir']
PARMnsem = os.environ['PARMnsem']
STORM = os.getenv('STORM')

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsWind.csv', header='infer', index_col="coordinate")

runPDY = base_info.tide_spin_end_date.strftime('%Y-%m-%d %H:%M')
print('Processing for runPDY: '+runPDY)

count=0
for station in stations.columns:
    df = pd.read_csv(PARMnsem+'/storms/'+STORM+'/'+str(station)+'h'+runPDY[0:4]+'.txt', skiprows=[1],  usecols=['#YY','MM','DD','hh','mm','WDIR','WSPD','GST','WTMP','WVHT'],delim_whitespace=True,na_values=[99.00,999.0])
    df['Date'] = pd.to_datetime(df['#YY'].astype(str)+df['MM'].astype(str).str.zfill(2)+df['DD'].astype(str).str.zfill(2)+' '+df['hh'].astype(str).str.zfill(2)+df['mm'].astype(str).str.zfill(2), format='%Y%m%d %H%M')
    df = df.rename(columns={'WSPD':station})
    df = df[['Date',station]]
    mask = (df['Date'] >= base_info.analysis_start_date.strftime('%Y-%m-%d')) & (df['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d'))
    df = df.loc[mask]
    df.set_index('Date', inplace=True)
    df = df.resample('H').mean()  # Resample to hourly
    print(df.head(10))
    if count==0:
       obs = df
    else:
       obs = pd.merge(obs, df, on='Date', how='inner')
    count+=1

print(obs.head(10))
obs.to_csv(PARMnsem+'/storms/'+STORM+"/ObsWind.txt", float_format="%.3f")
