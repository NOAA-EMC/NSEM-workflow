import os, sys
import pandas as pd

RUNdir = os.getenv('RUNdir')
USHnsem = os.getenv('USHnsem')
sys.path.append(USHnsem)
import nsem_ttest

model = pd.read_csv(RUNdir+'/ModelWind.txt', delim_whitespace=True)
obs = pd.read_csv(RUNdir+'/ObsWind.txt', delim_whitespace=True)

print(model.head())
print(obs.head())
print(model.shape[1])

for station in range(1,model.shape[1]-1):
   print('Processing '+model.columns[station])
   success, pvalue1, pvalue2 = nsem_ttest.test_90_accuracy(model.iloc[:,station],obs.iloc[:,station],plotflag=True,direc=RUNdir,label="HWRF_station"+model.columns[station],unit="U10 (m/s)")
   print(station, success, pvalue1, pvalue2)
