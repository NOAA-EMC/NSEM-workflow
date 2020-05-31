import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

RUNdir = os.getenv('RUNdir')
FIXnsem = os.getenv('FIXnsem')
USHnsem = os.getenv('USHnsem')
STORM = os.getenv('STORM')
sys.path.append(USHnsem)
import nsem_ttest
import nsem_utils

os.chdir(RUNdir)
print("Executing in", RUNdir)

def run_ttest(model, obs, label, units):
   
   p_array = np.zeros(model.shape[1]-1)
   success_array = np.zeros(model.shape[1]-1)
   
   for station in range(1,model.shape[1]):
      print('Processing '+model.columns[station])
      success, pvalue1, pvalue2 = nsem_ttest.test_90_accuracy(model.iloc[:,station],obs.iloc[:,station], \
                                                              plotflag=True,direc=RUNdir, \
                                                              label=label+"_station_"+model.columns[station],unit=units)
      print(station, success, pvalue1, pvalue2)
      p_array[station-1] = min(pvalue1, pvalue2)
      success_array[station-1] = success

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
   locations = pd.read_csv(RUNdir+'/ndbc_locations.txt', delim_whitespace=True)
   
   fig, ax = plt.subplots(figsize = [6.5, 5.5])
   plt.scatter(locations.iloc[:,2], locations.iloc[:,1], c=success_array, cmap='bwr_r')
    
   for i, txt in enumerate(locations.iloc[:,0]):
      ax.annotate(txt, (locations.iloc[i,2],locations.iloc[i,1]))
   plt.plot(landbound[:,0]-360., landbound[:,1], 'k', linewidth=1.0)
   plt.xlim([-90.00, -60.00])
   plt.ylim([10.00, 37.00])
   plt.rc('xtick',labelsize=14)
   plt.rc('ytick',labelsize=14)
   plt.title(label,fontsize=11)
   plt.savefig(RUNdir+"/ttest_map_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

   return p_array, success_array

# 1. Specify tests for covered data
# (a) HWRF winds
model = pd.read_csv(RUNdir+'/ModelWind.txt', delim_whitespace=True)
obs = pd.read_csv(RUNdir+'/ObsWind.txt', delim_whitespace=True)
label = "HWRF"
units = "U10 (m/s)"
### Clean obs data by setting all exception values (99.00) and zeros to nan, and forward-filling these values
obs = obs[obs < 99.00]
obs = obs[obs > 0.00]
obs = obs.fillna(method='ffill')
p_array, success_array = run_ttest(model, obs, label, units)
u10_best = model.columns[np.argmax(p_array)+1]  # First column is the date
u10_worst = model.columns[np.argmin(p_array)+1]  # First column is the date
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+u10_best)
print('Worst station is '+u10_worst)

# (b) WW3 Hs
model = pd.read_csv(RUNdir+'/ModelHs.txt', delim_whitespace=True)
obs = pd.read_csv(RUNdir+'/ObsHs.txt', delim_whitespace=True)
label = "WW3"
units = "Hs (m)"
p_array, success_array = run_ttest(model, obs, label, units)
hs_best = model.columns[np.argmax(p_array)+1]  # First column is the date
hs_worst = model.columns[np.argmin(p_array)+1]  # First column is the date
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+hs_best)
print('Worst station is '+hs_worst)

# 2. Compile automated validation report
# (a) Find best and worst performing stations in terms of p-values

# (b) Populate report by setting paths to result figures
dc_valreport={}
dc_valreport.update({'storm'                  :STORM })
dc_valreport.update({'date'                   :datetime.today().strftime('%B %e, %Y') })
dc_valreport.update({'fig_hwrf_summary'       :RUNdir+"/ttest_summary_HWRF.png" })
dc_valreport.update({'fig_hwrf_map'           :RUNdir+"/ttest_map_HWRF.png" })
dc_valreport.update({'fig_ww3_summary'        :RUNdir+"/ttest_summary_WW3.png" })
dc_valreport.update({'fig_ww3_map'            :RUNdir+"/ttest_map_WW3.png" })
dc_valreport.update({'fig_u10_ts_best'        :RUNdir+"/ttest_ts_HWRF_station_"+u10_best+".png" })
dc_valreport.update({'fig_u10_ts_worst'       :RUNdir+"/ttest_ts_HWRF_station_"+u10_worst+".png" })
dc_valreport.update({'fig_u10_hist_best'      :RUNdir+"/ttest_hist_HWRF_station_"+u10_best+".png" })
dc_valreport.update({'fig_u10_hist_worst'     :RUNdir+"/ttest_hist_HWRF_station_"+u10_worst+".png" })
dc_valreport.update({'fig_u10_scatter_best'   :RUNdir+"/ttest_scatter_HWRF_station_"+u10_best+".png" })
dc_valreport.update({'fig_u10_scatter_worst'  :RUNdir+"/ttest_scatter_HWRF_station_"+u10_worst+".png" })
dc_valreport.update({'fig_hs_ts_best'        :RUNdir+"/ttest_ts_WW3_station_"+hs_best+".png" })
dc_valreport.update({'fig_hs_ts_worst'       :RUNdir+"/ttest_ts_WW3_station_"+hs_worst+".png" })
dc_valreport.update({'fig_hs_hist_best'      :RUNdir+"/ttest_hist_WW3_station_"+hs_best+".png" })
dc_valreport.update({'fig_hs_hist_worst'     :RUNdir+"/ttest_hist_WW3_station_"+hs_worst+".png" })
dc_valreport.update({'fig_hs_scatter_best'   :RUNdir+"/ttest_scatter_WW3_station_"+hs_best+".png" })
dc_valreport.update({'fig_hs_scatter_worst'  :RUNdir+"/ttest_scatter_WW3_station_"+hs_worst+".png" })
##
tmpname = os.path.join(FIXnsem,'templates','validation_report.tex.tmpl')
val_report = os.path.join(RUNdir,'validation_report_'+STORM+'_'+datetime.today().strftime('%Y-%m-%d')+'.tex')
nsem_utils.tmp2scr(filename=val_report,tmpname=tmpname,d=dc_valreport)
# (c) Compile the validation report to PDF
os.system('pdflatex '+val_report)

