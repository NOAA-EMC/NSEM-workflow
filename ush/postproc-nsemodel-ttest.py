# ----------------------------------------------------------- 
# Python Script File
# Tested Operating System(s): RHEL 7, Python 3.7.5
# Tested Run Level(s): 
# Shell Used: BASH shell
# Original Author(s): Andre van der Westhuysen
# File Creation Date: 05/15/2020
# Date Last Modified:
#
# Version control: 1.00
#
# Support Team:
#
# Contributors: 
#
# ----------------------------------------------------------- 
# ------------- Program Description and Details ------------- 
# ----------------------------------------------------------- 
#
# Python script to perform 90% accuracy validation of NSEM output
#
# -----------------------------------------------------------

import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy	
import cartopy.crs as ccrs	
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

NSEMdir = os.environ['NSEMdir']
RUNdir = os.getenv('RUNdir')
PARMnsem = os.environ['PARMnsem']
FIXnsem = os.getenv('FIXnsem')
USHnsem = os.getenv('USHnsem')
STORM = os.getenv('STORM')
COMINobs = os.getenv('COMINobs')
sys.path.append(USHnsem)
import nsem_ttest
import nsem_utils

cartopy.config['pre_existing_data_dir'] = NSEMdir+'/lib/cartopy'
print('Reading cartopy shapefiles from:')
print(cartopy.config['pre_existing_data_dir'])

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

def run_ttest(model, obs, label, units):
   
   p_array = np.zeros(model.shape[1])
   success_array = np.zeros(model.shape[1])
   
   for station in range(0,model.shape[1]):
      print('Processing '+model.columns[station])
      if np.isnan(obs.iloc[:,station]).all():
         print('*** No observations at this station. Skipping.')
         p_array[station] = 0.00
         success_array[station] = 0
         continue
      success, pvalue1 = nsem_ttest.test_90_accuracy(model.iloc[:,station],obs.iloc[:,station], \
                                                     plotflag=True,direc=RUNdir, \
                                                     label=label+"_station_"+model.columns[station],unit=units)
      print(station, success, pvalue1)
      p_array[station] = pvalue1
      success_array[station] = success

   # Bar chart
   plt.figure(figsize = [6.4, 3.8])
   plt.rc('xtick',labelsize=8)
   plt.rc('ytick',labelsize=8)
   plt.bar(model.columns[:],p_array)
   plt.axhline(y=0.05,linewidth=1, color='r')
   plt.yscale('log')
   plt.xticks(rotation=90)
   plt.xlabel("Stations",fontsize=9)
   plt.ylabel("p-value (Prob of falsely rejecting H0, while true)",fontsize=9)
   plt.title(label,fontsize=11)
   plt.savefig(RUNdir+"/ttest_summary_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)
   
   # Map display
   if label=="ATM":
      stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsWind.csv', header='infer', index_col="coordinate") 
   if label=="P":
      stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsPres.csv', header='infer', index_col="coordinate")
   if label=="WW3":
      stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsHs.csv', header='infer', index_col="coordinate")
   if label=="ADC":
      stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsWLV.csv', header='infer', index_col="coordinate")
   besttrack = pd.read_csv(PARMnsem+'/storms/'+STORM+'/best_track.txt', header=None, skiprows=4, delim_whitespace=True)

   ax = plt.axes(projection=ccrs.PlateCarree())
   ax.set_extent([base_info.lonmin_plot_landfall, base_info.lonmax_plot_landfall, 
                  base_info.latmin_plot_landfall, base_info.latmax_plot_landfall], ccrs.PlateCarree())
   coast = cfeature.GSHHSFeature(scale='high',edgecolor='black',facecolor='none',linewidth=0.25)	
   ax.add_feature(coast)
   for i, txt in enumerate(stations.columns):
      ax.annotate(txt, (stations.iloc[0,i]+0.05, stations.iloc[1,i]+0.05), fontsize=8)
      if success_array[i]==1:
         plt.plot(stations.iloc[0,i], stations.iloc[1,i],  markersize=4, marker='o', color='red')
      else:
         plt.plot(stations.iloc[0,i], stations.iloc[1,i],  markersize=4, marker='o', color='blue')
   plt.plot(besttrack.iloc[:,3].values, besttrack.iloc[:,2].values, 'k--', linewidth=1.0)
   gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                     linewidth=2, color='gray', alpha=0.5, linestyle=None)
   gl.xlabels_top = False
   gl.ylabels_right = False
   gl.xlines = False
   gl.ylines = False
   gl.xformatter = LONGITUDE_FORMATTER
   gl.yformatter = LATITUDE_FORMATTER
   gl.xlabel_style = {'size': 7, 'color': 'black'}
   gl.ylabel_style = {'size': 7, 'color': 'black'}
   figtitle = units+' 90% accuracy assessment'
   plt.title(figtitle)
   plt.savefig(RUNdir+"/ttest_map_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

   return p_array, success_array

print('--- In: postproc-nsemodel-ttest.py ---')
os.makedirs(RUNdir, exist_ok=True)
os.chdir(RUNdir)
print("Executing in", RUNdir)

# 1. Specify tests for covered data
# (a) ATM winds
print('\nAssessing Wind results...')
os.system('cp -f ' + COMINobs + '/ObsWind.csv ' + RUNdir + '/')
if os.path.exists(COMINobs + '/ModelWind.csv'):
   print('*** Copying wind file to run directory')
   os.system('cp -f ' + COMINobs + '/ModelWind.csv ' + RUNdir + '/')
model = pd.read_csv(RUNdir+'/ModelWind.csv', header='infer')
obs = pd.read_csv(RUNdir+'/ObsWind.csv', header='infer')
label = "ATM"
units = "U10 (m/s)"
### Clean obs data by setting all exception values (99.00) and zeros to nan, and forward-filling these values
obs = obs[obs < 99.00]
obs = obs[obs > 0.00]
obs = obs.fillna(method='ffill')
mask = (model['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (model['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
model = model.loc[mask]
model['Date'] = pd.to_datetime(model['Date']) #AW
model.set_index('Date', inplace=True)
mask = (obs['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (obs['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
obs = obs.loc[mask]
obs['Date'] = pd.to_datetime(obs['Date']) #AW
obs.set_index('Date', inplace=True)
print(model.head(20))
print(model.tail(20))
print(obs.head(20))
print(obs.tail(20))
p_array, success_array = run_ttest(model, obs, label, units)
u10_best = model.columns[np.argmax(p_array)]
u10_worst = model.columns[np.argmin(p_array)]
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+u10_best)
print('Worst station is '+u10_worst)

# (b) ATM pressure
print('\nAssessing Pres results...')
os.system('cp -f ' + COMINobs + '/ObsPres.csv ' + RUNdir + '/')
model = pd.read_csv(RUNdir+'/ModelPres.csv', header='infer')
obs = pd.read_csv(RUNdir+'/ObsPres.csv', header='infer')
label = "P"
units = "Sfc Press (mb)"
### Clean obs data by setting all exception values (99.00) and zeros to nan, and forward-filling these values
#obs = obs[obs < 9999.00]
obs = obs[obs > 0.00]
obs = obs.fillna(method='ffill')
mask = (model['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (model['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
model = model.loc[mask]
#model.iloc[:,:] = model.iloc[:,:]*100. #Convert hPa to Pa
model['Date'] = pd.to_datetime(model['Date']) #AW
model.set_index('Date', inplace=True)
mask = (obs['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (obs['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
obs = obs.loc[mask]
obs['Date'] = pd.to_datetime(obs['Date']) #AW
obs.set_index('Date', inplace=True)
print(model.head(20))
print(model.tail(20))
print(obs.head(20))
print(obs.tail(20))
array, success_array = run_ttest(model, obs, model2, model3, label, units)
p_best = model.columns[np.argmax(p_array)]
p_worst = model.columns[np.argmin(p_array)]
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+p_best)
print('Worst station is '+p_worst)

# (c) WW3 Hs
print('\nAssessing Hs results...')
os.system('cp -f ' + COMINobs + '/ObsHs.csv ' + RUNdir + '/')
model = pd.read_csv(RUNdir+'/ModelHs.csv', header='infer')
obs = pd.read_csv(RUNdir+'/ObsHs.csv', header='infer')
label = "WW3"
units = "Hs (m)"
### Clean obs data by setting all exception values (99.00) and zeros to nan, and forward-filling these values
obs = obs[obs < 99.00]
obs = obs[obs > 0.00]
obs = obs.fillna(method='ffill')
mask = (model['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (model['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
model = model.loc[mask]
model['Date'] = pd.to_datetime(model['Date']) #AW
model.set_index('Date', inplace=True)
mask = (obs['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (obs['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
obs = obs.loc[mask]
obs['Date'] = pd.to_datetime(obs['Date']) #AW
obs.set_index('Date', inplace=True)
print(model.head(20))
print(model.tail(20))
print(obs.head(20))
print(obs.tail(20))
p_array, success_array = run_ttest(model, obs, label, units)
hs_best = model.columns[np.argmax(p_array)]  # First column is the date
hs_worst = model.columns[np.argmin(p_array)]  # First column is the date
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+hs_best)
print('Worst station is '+hs_worst)

# (d) WW3 WLV
print('\nAssessing WLV results...')
os.system('cp -f ' + COMINobs + '/ObsWLV.csv ' + RUNdir + '/')
model = pd.read_csv(RUNdir+'/ModelWLV.csv', header='infer')
obs = pd.read_csv(RUNdir+'/ObsWLV.csv', header='infer')
obs = obs[obs < 9999.00]
obs = obs.fillna(method='ffill')
model = model.fillna(method='ffill')
label = "ADC"
units = "WL (m MSL)"
mask = (model['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (model['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
model = model.loc[mask]
model['Date'] = pd.to_datetime(model['Date']) #AW
model.set_index('Date', inplace=True)
mask = (obs['Date'] > base_info.analysis_start_date.strftime('%Y-%m-%d %H:%M:%S')) & (obs['Date'] <= base_info.analysis_end_date.strftime('%Y-%m-%d %H:%M:%S'))
obs = obs.loc[mask]
obs['Date'] = pd.to_datetime(obs['Date']) #AW
obs.set_index('Date', inplace=True)
print(model.head(20))
print(model.tail(20))
print(obs.head(52))
print(obs.tail(20))
obs.to_csv(RUNdir+"/ObsWLV_check.csv")
model.to_csv(RUNdir+"/ModelWLV_check.csv")
p_array, success_array = run_ttest(model, obs, label, units)
wlv_best = model.columns[np.argmax(p_array)]  # First column is the date
wlv_worst = model.columns[np.argmin(p_array)]  # First column is the date
print('All stations:')
print(model.columns)
print('p-values for all stations:')
print(p_array)
print('Pass (1) or fail (0) for all stations:')
print(success_array)
print('Best station is '+wlv_best)
print('Worst station is '+wlv_worst)

"""
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
"""

