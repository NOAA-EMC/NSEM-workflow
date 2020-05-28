import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RUNdir = os.getenv('RUNdir')
USHnsem = os.getenv('USHnsem')
sys.path.append(USHnsem)
import nsem_ttest

### User inputs ##################
model = pd.read_csv(RUNdir+'/ModelWind.txt', delim_whitespace=True)
obs = pd.read_csv(RUNdir+'/ObsWind.txt', delim_whitespace=True)
label = "HWRF"
units = "U10 (m/s)"
#model = pd.read_csv(RUNdir+'/ModelHs.txt', delim_whitespace=True)
#obs = pd.read_csv(RUNdir+'/ObsHs.txt', delim_whitespace=True)
#label = "WW3"
#units = "Hs (m)"

locations = pd.read_csv(RUNdir+'/ndbc_locations.txt', delim_whitespace=True)
##################################

print(model.head())
print(obs.head())
print(locations.head())

p_array = np.zeros(model.shape[1]-1)

for station in range(1,model.shape[1]):
   print('Processing '+model.columns[station])
   success, pvalue1, pvalue2 = nsem_ttest.test_90_accuracy(model.iloc[:,station],obs.iloc[:,station], \
                                                           plotflag=True,direc=RUNdir, \
                                                           label=label+"_station_"+model.columns[station],unit=units)
   print(station, success, pvalue1, pvalue2)
   p_array[station-1] = min(pvalue1, pvalue2)

print(p_array)

# Bar chart
plt.figure(figsize = [6.4, 3.8])
plt.bar(model.columns[1:],p_array)
plt.axhline(y=0.05,linewidth=1, color='r')
plt.yscale('log')
plt.rc('xtick',labelsize=3)
plt.xticks(rotation=90)
plt.rc('ytick',labelsize=3)
plt.xlabel("Stations",fontsize=9)
plt.ylabel("p-value (Prob of falsely rejecting H0, while true)",fontsize=9)
plt.title(label,fontsize=11)
plt.savefig(RUNdir+"/ttest_summary_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

# Map display
landbound = np.loadtxt(USHnsem+'/coastal_bound_high.txt')
success = p_array > 0.05

fig, ax = plt.subplots(figsize = [6.5, 5.5])
plt.scatter(locations.iloc[:,2], locations.iloc[:,1], c=success, cmap='bwr_r')

for i, txt in enumerate(locations.iloc[:,0]):
    ax.annotate(txt, (locations.iloc[i,2],locations.iloc[i,1]))
plt.plot(landbound[:,0]-360., landbound[:,1], 'k', linewidth=1.0)
plt.xlim([-90.00, -60.00])
plt.ylim([10.00, 37.00])
plt.rc('xtick',labelsize=14)
plt.rc('ytick',labelsize=14)
plt.title(label,fontsize=11)
plt.savefig(RUNdir+"/ttest_map_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

