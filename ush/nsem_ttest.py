# ----------------------------------------------------------- 
# Python Script File
# Tested Operating System(s): RHEL 7, Python 3.7.5
# Tested Run Level(s): 
# Shell Used: BASH shell
# Original Author(s): Andre van der Westhuysen
# File Creation Date: 08/26/2019
# Date Last Modified:
#
# Version control: 1.00
#
# Support Team:
#
# Contributors: Andre van der Westhuysen
#
# ----------------------------------------------------------- 
# ------------- Program Description and Details ------------- 
# ----------------------------------------------------------- 
#
# Python module for comouting statistical t-test
#
# -----------------------------------------------------------

import matplotlib
matplotlib.use('Agg',warn=False)

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

def test_90_accuracy(model, observations, plotflag=False, direc="", label="model", unit="Value"):
# Function to perform the 90% accuracy test for FEMA using
# a paired t-test on the model output and observations.

   obs1 = observations
   mod1 = model 
   print(obs1.head(20))
   print(obs1.tail(20))
   print(mod1.head(20))
   print(mod1.tail(20))  

   # Perform a paired t-test
   m = 0.1
   alpha = 0.05
   #print("mean = "+str(np.mean((mod1-obs1)/obs1))+", stdev = "+str(stats.tstd((mod1-obs1)/obs1)))
   #if np.mean((mod1-obs1)/obs1) > 0:
   if np.mean(np.abs(mod1-obs1)/np.max(obs1)) > 0:
      # Alternative hypothesis: mu_drel > 0.1 (right-tailed test)
      print("Testing Ha: mu_drel > "+str(m))
      results = stats.ttest_1samp(np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01), m)
      #print(results[0],results[1])
      if (results[0] > 0) & (results[1]/2 < alpha):
         pvalue1 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue1))
         print("reject null hypothesis, mean is more than "+str(m))
         test1 = 0
      else:
         if (results[0] > 0):
            pvalue1 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         else:
            pvalue1 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         print("accept null hypothesis")
         test1 = 1
   else:
      # Alternative hypothesis: mu_drel < -0.1 (left-tailed test)
      print("Testing Ha: mu_drel < "+str(-m))
      results = stats.ttest_1samp(np.abs(mod1-obs1)/np.maximum(obs1,0.01), -m)
      #print(results[0],results[1])
      if (results[0] < 0) & (results[1]/2 < alpha):
         pvalue1 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue1))
         print("reject null hypothesis, mean is less than "+str(-m))
         test1 = 0
      else:
         if (results[0] < 0):
            pvalue1 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         else:
            pvalue1 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))         
         print("accept null hypothesis")   
         test1 = 1

   # Compare with Simple Linear Regression
   model = np.array(model)
   observations = np.array(observations)
   linreg = LinearRegression(fit_intercept=False)  # Regression through origin
   linreg.fit(observations[:, np.newaxis],model[:, np.newaxis])
   y_pred = linreg.predict(observations[:, np.newaxis])
   intercept = 0. #linreg.intercept_[0]
   slope = float(linreg.coef_[0])
   rmse = np.sqrt(metrics.mean_squared_error(model[:, np.newaxis],y_pred))
   si = rmse/np.mean(observations)
   #print("Intercept ="+str(intercept))
   #print("Slope ="+str(slope))
   #print("RMSE = "+str(rmse))
   #print("SI = "+str(si)) 
         
   if (test1 == 1):
      success = 1
      print(" => 90% accuracy criterion is met.")
   else:
      success = 0
      print(" => 90% accuracy criterion is NOT met.")
   #print("Range of rel_d1 = ["+str(min((mod1-obs1)/obs1))+", "+str(max((mod1-obs1)/obs1))+"]")
   #print("Range of rel_d2 = ["+str(min((mod2-obs2)/obs2))+", "+str(max((mod2-obs2)/obs2))+"]")

   """
   # Plot the time series
   if plotflag:
      plt.clf()
      #fig, axs = plt.subplots(2)
      fig = plt.figure(figsize=(10,2), dpi=300)
      #fig, ax = plt.subplots()
      plt.plot(obs1, 'k-o', markerfacecolor='w', markeredgecolor='k', markersize=3, label='Observations')
      plt.plot(mod1, 'b-', label='Model')
      plt.plot(10.*np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01), 'r-', label='d*10')
      print(np.mean(np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01)))
      plt.plot((10.*np.mean(np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01))+0.*obs1), 'r--', label='mean(d*10)')
      plt.legend()
      plt.plot(0.9*obs1, 'k--', linewidth=0.5)
      plt.plot(1.1*obs1, 'k--', linewidth=0.5)
      plt.plot(0.0*mod1, 'k:', linewidth=0.5)
      plt.grid()
      plt.ylabel(unit) 
      plt.title(label+": p-values = "+"{:.3f}".format(pvalue1))
      plt.ylim([min(1.2*min(min(obs1),min(mod1)), 0.), 1.2*max(max(obs1),max(mod1))])
      plt.xlabel("Date (MM-DD HH)")
      plt.ylabel(unit)
      #dtFmt = mdates.DateFormatter('%d')
      #ax.xaxis_date()
      #ax.xaxis.set_major_formatter(dtFmt)
      #plt.gca().xaxis.set_major_formatter(dtFmt)
      plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %HH:%MM'))
      plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
      plt.gcf().autofmt_xdate()
      plt.tick_params(axis='x', labelsize=9, labelrotation=45)
      plt.savefig(direc+"/ttest_ts_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

      plt.figure(figsize=(60,20), dpi=300)
      date_form = DateFormatter("%Y-%m-%d %HH:%MM")
      fig, axs = plt.subplots(5, gridspec_kw={'hspace': 0.5})
      axs[4].plot(obs1, 'k-o', markerfacecolor='w', markeredgecolor='k', markersize=3, label='Observations')
      axs[4].plot(mod1, 'b-', label='Model')
      #axs[4].set_xlim(pd.Timestamp('2020-01-01'), pd.Timestamp('2020-12-31'))
      axs[4].xaxis.set_major_formatter(date_form)
      axs[4].set(xlabel='Date', ylabel='Hm0 (m)')
      axs[4].tick_params(labelsize=8)
      axs[4].yaxis.get_label().set_fontsize(8)
      plt.savefig(direc+'/rip_current_obs_avail_ts.png', dpi=300, bbox_inches='tight')
   """

   # Plot the time series
   if plotflag:
      if (unit=="U10 (m/s)") or (unit=="Hs (m)"):
         plotscale=10.
         plotlabel1='d*10'
         plotlabel2='mean(d*10)'
      else:
         plotscale=1.
         plotlabel1='d'
         plotlabel2='mean(d)'
      plt.clf()
      #fig, axs = plt.subplots(2)
      fig = plt.figure(figsize=(20,4), dpi=300)
      plt.plot(obs1, 'k-o', markerfacecolor='w', markeredgecolor='k', markersize=3, label='Observations')
      plt.plot(mod1, 'b-', label='Model')
      plt.plot(plotscale*np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01), 'r-', label=plotlabel1)
      print(np.mean(np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01)))
      plt.plot((plotscale*np.mean(np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01))+0.*obs1), 'r--', label=plotlabel2)
      plt.legend()
      plt.plot(0.9*obs1, 'k--', linewidth=0.5)
      plt.plot(1.1*obs1, 'k--', linewidth=0.5)
      plt.plot(0.0*mod1, 'k:', linewidth=0.5)
      plt.grid()
      plt.ylabel(unit) 
      plt.title(label+": p-values = "+"{:.3f}".format(pvalue1))
      plt.ylim([min(1.2*min(min(obs1),min(mod1)), 0.), 1.2*max(max(obs1),max(mod1))])
      plt.xlabel("Date (MM-DD HH)")
      plt.ylabel(unit)
      plt.tick_params(axis='x', labelsize=9, labelrotation=45)
      plt.tick_params(axis='y', labelsize=9)
      plt.savefig(direc+"/ttest_ts_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

   # Plot the histogram of the difference d
   if plotflag:
      d1 = np.abs(mod1-obs1)/np.maximum(np.max(obs1),0.01)
      maxdev = max(d1)
      plt.clf()
      fig = plt.figure(figsize=(5,5), dpi=300)
      plt.hist(d1, 20)
      plt.xlabel("d", fontsize=12)
      plt.ylabel("Frequency", fontsize=12) 
      plt.xticks(fontsize=10)
      plt.yticks(fontsize=10)
      plt.xlim([-(maxdev+0.1),maxdev+0.1])
      plt.title(label+": p-values = "+"{:.3f}".format(pvalue1))
      plt.text(0.2, 0.8, "n="+str(len(d1)), transform=fig.transFigure)
      plt.savefig(direc+"/ttest_hist_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)
      
   if plotflag:
      plt.clf()
      fig = plt.figure(figsize=(5,5), dpi=300)
      plt.plot(observations, model, 'ko', markersize=2)
      plt.plot(observations, intercept + observations*slope, 'k-')
      plt.plot([0, max(max(model), max(observations))], [0, max(max(model), max(observations))], 'k--')
      plt.plot([0, max(max(model), max(observations))], [0, 0.9*max(max(model), max(observations))], 'k:')
      plt.plot([0, max(max(model), max(observations))], [0, 1.1*max(max(model), max(observations))], 'k:')
      plt.xlabel("obs", fontsize=12)
      plt.ylabel("mod", fontsize=12)
      plt.xticks(fontsize=10)
      plt.yticks(fontsize=10)
      plt.xlim([0, max(max(model), max(observations))])
      plt.ylim([0, max(max(model), max(observations))])
      plt.gca().set_aspect('equal', adjustable='box')
      plt.text(0.15, 0.8, "Slope="+"{:.3f}".format(slope), transform=fig.transFigure, fontsize=12)
      plt.text(0.15, 0.7, "RMSE="+"{:.4f}".format(rmse), transform=fig.transFigure, fontsize=12)
      plt.text(0.15, 0.6, "SI="+"{:.4f}".format(si), transform=fig.transFigure, fontsize=12)
      plt.savefig(direc+"/ttest_scatter_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1) 
   
   return success, pvalue1

def test_90_accuracy_2part(model, observations, plotflag=False, direc="", label="model", unit="Value"):
# Function to perform the 90% accuracy test for FEMA using
# a paired t-test on the model output and observations.
# Data is partitioned into a subset before and after the 
# storm peak in order to detect errors due to time lag.

   # Split the data into segments before and after the storm peak
   cuttime = observations.idxmax(axis=1)
   print("Split ts at index of max obs: "+str(cuttime))
   obs1 = observations[:cuttime]
   mod1 = model[:cuttime]
   obs2 = observations[cuttime:]
   mod2 = model[cuttime:]
    
   # Perform a paired t-test on the increasing ts segment
   m = 0.1
   alpha = 0.05
   #print("mean = "+str(np.mean((mod1-obs1)/obs1))+", stdev = "+str(stats.tstd((mod1-obs1)/obs1)))
   if np.mean((mod1-obs1)/obs1) > 0:
      # Alternative hypothesis: mu_drel > 0.1 (right-tailed test)
      print("Testing Ha: mu_drel > "+str(m))
      results = stats.ttest_1samp((mod1-obs1)/np.maximum(obs1,0.01), m)
      #print(results[0],results[1])
      if (results[0] > 0) & (results[1]/2 < alpha):
         pvalue1 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue1))
         print("reject null hypothesis, mean is more than "+str(m))
         test1 = 0
      else:
         if (results[0] > 0):
            pvalue1 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         else:
            pvalue1 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         print("accept null hypothesis")
         test1 = 1
   else:
      # Alternative hypothesis: mu_drel < -0.1 (left-tailed test)
      print("Testing Ha: mu_drel < "+str(-m))
      results = stats.ttest_1samp((mod1-obs1)/np.maximum(obs1,0.01), -m)
      #print(results[0],results[1])
      if (results[0] < 0) & (results[1]/2 < alpha):
         pvalue1 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue1))
         print("reject null hypothesis, mean is less than "+str(-m))
         test1 = 0
      else:
         if (results[0] < 0):
            pvalue1 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))
         else:
            pvalue1 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue1))         
         print("accept null hypothesis")   
         test1 = 1

   # Perform a paired t-test on the decreasing ts segment  
   #print("mean = "+str(np.mean((mod2-obs2)/obs2))+", stdev = "+str(stats.tstd((mod2-obs2)/obs2)))
   if np.mean((mod2-obs2)/obs2) > 0:
      # Alternative hypothesis: mu_drel > 0.1 (right-tailed test)
      print("Testing Ha: mu_drel > "+str(m))
      results = stats.ttest_1samp((mod2-obs2)/np.maximum(obs2,0.01), m)
      #print(results[0],results[1])
      if (results[0] > 0) & (results[1]/2 < alpha):
         pvalue2 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue2))
         print("reject null hypothesis, mean is more than "+str(m))
         test2 = 0
      else:
         if (results[0] > 0):
            pvalue2 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue2))
         else:
            pvalue2 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue2))
         print("accept null hypothesis")
         test2 = 1
   else:
      # Alternative hypothesis: mu_drel < -0.1 (left-tailed test)
      print("Testing Ha: mu_drel < "+str(-m))
      results = stats.ttest_1samp((mod2-obs2)/np.maximum(obs2,0.01), -m)
      #print(results[0],results[1])
      if (results[0] < 0) & (results[1]/2 < alpha):
         pvalue2 = results[1]/2
         print('p-value = '+"{:.5f}".format(pvalue2))
         print("reject null hypothesis, mean is less than "+str(-m))
         test2 = 0
      else:
         if (results[0] < 0):
            pvalue2 = results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue2))
         else:
            pvalue2 = 1-results[1]/2
            print('p-value = '+"{:.5f}".format(pvalue2))         
         print("accept null hypothesis")   
         test2 = 1

   # Compare with Simple Linear Regression
   model = np.array(model)
   observations = np.array(observations)
   linreg = LinearRegression(fit_intercept=False)  # Regression through origin
   linreg.fit(observations[:, np.newaxis],model[:, np.newaxis])
   y_pred = linreg.predict(observations[:, np.newaxis])
   intercept = 0. #linreg.intercept_[0]
   slope = float(linreg.coef_[0])
   rmse = np.sqrt(metrics.mean_squared_error(model[:, np.newaxis],y_pred))
   si = rmse/np.mean(observations)
   #print("Intercept ="+str(intercept))
   #print("Slope ="+str(slope))
   #print("RMSE = "+str(rmse))
   #print("SI = "+str(si)) 
         
   if (test1 == 1 and test2 == 1):
      success = 1
      print(" => 90% accuracy criterion is met.")
   else:
      success = 0
      print(" => 90% accuracy criterion is NOT met.")
   #print("Range of rel_d1 = ["+str(min((mod1-obs1)/obs1))+", "+str(max((mod1-obs1)/obs1))+"]")
   #print("Range of rel_d2 = ["+str(min((mod2-obs2)/obs2))+", "+str(max((mod2-obs2)/obs2))+"]")

   # Plot the time series
   if plotflag:
      plt.clf()
      fig, axs = plt.subplots(2)
      axs[0].plot(obs1, 'k-o', markerfacecolor='w', markeredgecolor='k', markersize=3, label='Observations')
      axs[0].plot(mod1, 'b-', label='Model')
      axs[0].legend()
      axs[0].plot(0.9*obs1, 'k--', linewidth=0.5)
      axs[0].plot(1.1*obs1, 'k--', linewidth=0.5)
      axs[0].plot(0.0*mod1, 'k:', linewidth=0.5)
      axs[0].set(ylabel=unit, title=label+": p-values = "+"{:.3f}".format(pvalue1)+"; "+"{:.3f}".format(pvalue2))
      axs[0].set(ylim=[min(1.2*min(min(obs1),min(mod1)), 0.), 1.2*max(max(obs1),max(mod1))])
      axs[0].tick_params(axis='x', labelsize=9 )
      axs[1].plot(obs2, 'k-o', markerfacecolor='w', markeredgecolor='k', markersize=3, label='Observations')
      axs[1].plot(mod2, 'b-', label='Model')
      axs[1].legend()
      axs[1].plot(0.9*obs2, 'k--', linewidth=0.5)
      axs[1].plot(1.1*obs2, 'k--', linewidth=0.5)
      axs[1].plot(0.0*mod2, 'k:', linewidth=0.5)
      axs[1].set(xlabel="Time (h)", ylabel=unit)
      axs[1].set(ylim=[min(1.2*min(min(obs2),min(mod2)), 0.), 1.2*max(max(obs2),max(mod2))])
      axs[1].tick_params(axis='x', labelsize=9 )
      plt.savefig(direc+"/ttest_ts_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)

   # Plot the histogram of the difference d
   if plotflag:
      d1 = mod1 - obs1
      d2 = mod2 - obs2
      maxdev = max(max(d1),max(d2))
      plt.clf()
      fig, axs = plt.subplots(2)
      axs[0].hist(d1, 20)
      axs[0].set(ylabel="Frequency", xlim=[-(maxdev+1),maxdev+1], title=label+": p-values = "+"{:.3f}".format(pvalue1)+"; "+"{:.3f}".format(pvalue2))
      axs[0].text(0.05, 0.8, "n="+str(len(d1)), transform = axs[0].transAxes)
      axs[1].hist(d2, 20)
      axs[1].set(xlabel="d", ylabel="Frequency", xlim=[-(maxdev+1),maxdev+1])
      axs[1].text(0.05, 0.8, "n="+str(len(d2)), transform = axs[1].transAxes)
      plt.savefig(direc+"/ttest_hist_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1)
      
   if plotflag:
      plt.clf()
      plt.plot(observations, model, 'ko', markersize=2)
      plt.plot(observations, intercept + observations*slope, 'k-')
      plt.plot([0, max(observations)], [0, max(observations)], 'k--')
      plt.plot([0, max(observations)], [0, 0.9*max(observations)], 'k:')
      plt.plot([0, max(observations)], [0, 1.1*max(observations)], 'k:')
      plt.xlabel("obs", fontsize=12)
      plt.ylabel("mod", fontsize=12)
      plt.xlim([0, max(max(model), max(observations))])
      plt.ylim([0, max(max(model), max(observations))])
      plt.gca().set_aspect('equal', adjustable='box')
      plt.text(0.15, 0.8, "Slope="+"{:.3f}".format(slope), transform = axs[0].transAxes, fontsize=12)
      plt.text(0.15, 0.6, "RMSE="+"{:.4f}".format(rmse), transform = axs[0].transAxes, fontsize=12)
      plt.text(0.15, 0.4, "SI="+"{:.4f}".format(si), transform = axs[0].transAxes, fontsize=12)
      plt.savefig(direc+"/ttest_scatter_"+label+".png",dpi=150,bbox_inches='tight',pad_inches=0.1) 
   
   return success, pvalue1, pvalue2

if __name__ == '__main__':
   # Read and select example data
   stations = ["NDBC41002","NDBC41010","NDBC41009","NDBC41008","NDBC41004","NDBC42039","NDBC42036"]
   for s in stations:
      print("\nEvaluating station: "+s)
      mod_raw = pd.read_csv(direc+"Wind_Model_"+s+"_20170905000000_20170912050000.txt", header=None, names=["Model"])
      obs_raw = pd.read_csv(direc+"Wind_Obs_"+s+"_20170905000000_20170912050000.txt", header=None, names=["Obs"])
      mod = mod_raw["Model"]
      obs = obs_raw["Obs"]
      # Resample the 10-min data to 1-hourly data
      mod = mod[mod.index[::6]].reset_index(drop=True)
      obs = obs[obs.index[::6]].reset_index(drop=True)
      mod = mod[mod.index[24:]].reset_index(drop=True)
      obs = obs[obs.index[24:]].reset_index(drop=True)
      success, pvalue1, pvalue2 = ttest_90_accuracy(mod,obs,plotflag=True,label=s,unit="U10 (m/s)")
      print(success, pvalue1, pvalue2)

