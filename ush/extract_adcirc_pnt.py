# Script for plotting unstructured WW3 output files in netCDF format, created by ww3_ounf
# Andre van der Westhuysen, 09/08/20
#
import matplotlib
matplotlib.use('Agg',warn=False)

import os
import sys
import datetime
import pandas as pd
from matplotlib.tri import Triangulation, TriAnalyzer, LinearTriInterpolator
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import cartopy	
import cartopy.crs as ccrs	
import cartopy.feature as cfeature

NSEMdir = os.environ['NSEMdir']
RUNdir = os.getenv('RUNdir')
PARMnsem = os.getenv('PARMnsem')
FIXnsem = os.getenv('FIXnsem')
EXECnsem = os.getenv('EXECnsem')
COMOUT = os.getenv('COMOUT')
STORM = os.getenv('STORM')
RUN_TYPE = os.getenv('RUN_TYPE')

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

def extract_wlv(storm, datafile1, stations, df, lonmin=None, lonmax=None, latmin=None, latmax=None):

   print('Reading', datafile1)
   #Single file netCDF reading
   #ncf='ww3.field.2018_wnd.nc'
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)
   #ncf2='ww3.field.2018_dp.nc'
   #ncf2=datafile2
   #nco2=netCDF4.Dataset(ncf2)

   #Get fields to plot
   lon=nco.variables['x'][:]
   lat=nco.variables['y'][:]
   pnt_lon=stations.iloc[0,:].values
   pnt_lat=stations.iloc[1,:].values 
   timeinsec=nco.variables['time'][:]
   #base_date=nco.variables['time:base_date']
   #print(base_date)
   wlv=nco.variables['zeta'][:]
   triangles=nco.variables['element'][:,:]

   #timeindays2=nco2.variables['time'][:]
   #dir=nco2.variables['dp'][:]

   if lonmin != None:
      reflon=np.linspace(lonmin, lonmax, 1000)
      reflat=np.linspace(latmin, latmax, 1000)
   else:
      reflon=np.linspace(lon.min(),lon.max(),1000)
      reflat=np.linspace(lat.min(),lat.max(),1000)
   reflon,reflat=np.meshgrid(reflon,reflat)

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   triangles=triangles-1  # Correct indices for Python's zero-base
   tri=Triangulation(lon,lat,triangles=triangles)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   #Read obs point locations
   #data=np.loadtxt('erie_ndbc.loc', comments = '$')
   #buoylon=data[:,0]
   #buoylat=data[:,1]

   df_dates = pd.DataFrame(columns = ['Date'])

   # Loop through each time step and plot results
   for ind in range(0, len(timeinsec)):
      #plt.clf()
      #ax = plt.axes(projection=ccrs.Mercator())

      dt = base_info.tide_spin_start_date + datetime.timedelta(seconds=timeinsec[ind])
      dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
      dstr = dstr[0:8]+' '+dstr[8:17]
      print('Plotting '+dstr)

      par=np.double(wlv[ind,:])

      tli=LinearTriInterpolator(tri,par)
      par_interp=tli(pnt_lon,pnt_lat)

      #print(par_interp)
      df.loc[len(df)] = par_interp
      df_dates.loc[len(df_dates)] = pd.to_datetime(dt, format="%Y-%m-%d %H:%M:%S")
      #line = pd.to_datetime(dt, format="%Y-%m-%d %H:%M:%S")
      #new_row = pd.DataFrame(par_interp, columns=stations.columns, index=line)
      #df = pd.concat([df, pd.DataFrame(new_row)], ignore_index=False)

      del(par)
      del(par_interp)

   df['Date']=df_dates
   df.set_index('Date', inplace=True)
   return df

def extract_wlv_pnt(storm, datafile1, stations, df):

   print('Reading', datafile1)
   #Single file netCDF reading
   #ncf='ww3.field.2018_wnd.nc'
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)
   #ncf2='ww3.field.2018_dp.nc'
   #ncf2=datafile2
   #nco2=netCDF4.Dataset(ncf2)

   #Get fields to plot
   lon=nco.variables['x'][:]
   lat=nco.variables['y'][:]
   station_name=nco.variables['station_name'][:]
   timeinsec=nco.variables['time'][:].filled()
   zeta=nco.variables['zeta'][:]
   #print(timeinsec)

   statname = np.zeros(station_name.shape[0])

   for i in range(0, station_name.shape[0]):
      statname[i] = station_name[i,:].tostring().decode('UTF-8').strip()
   df = pd.DataFrame(zeta, columns = np.int_(statname))

   df_dates = pd.DataFrame(columns = ['Date'])
   for i in range(0, timeinsec.shape[0]):
      dt = base_info.tide_spin_start_date + datetime.timedelta(seconds=timeinsec[i])
      df_dates.loc[len(df_dates)] = pd.to_datetime(dt, format="%Y-%m-%d %H:%M:%S")

   df['Date']=df_dates
   df = df.set_index('Date')
   #print(df.head(10))
   df = df.resample('H').mean()  # Resample to hourly
   #print(df.head(10))
   integer_map = map(int, stations.columns)
   station_list = list(integer_map)
   df = df[station_list]
   print(df.head(10))

   return df

if __name__ == "__main__":
   print('--- In: extract_adcirc_pnt.py ---')
   runPDY = base_info.tide_spin_end_date.strftime('%Y-%m-%d %H:%M')
   print('Processing for runPDY: '+runPDY)
   """
   print('\nExtracting WLV output from ADCIRC...')
   stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsWLV.csv', header='infer', index_col="coordinate")
   df = pd.DataFrame(columns = stations.columns)
   extract_wlv(storm=STORM, datafile1=RUNdir+'/fort.63.nc', stations=stations, df=df,
               lonmin=base_info.lonmin_plot_landfall,
               lonmax=base_info.lonmax_plot_landfall,
               latmin=base_info.latmin_plot_landfall,
               latmax=base_info.latmax_plot_landfall)
   #df.to_pickle(RUNdir+"ModelWLV.pkl")
   df.to_csv(RUNdir+"/ModelWLV.txt")
   """

   print('\nExtracting WLV output from ADCIRC...')
   stations = pd.read_csv(PARMnsem+'/storms/'+STORM+'/StationsWLV.csv', header='infer', index_col="coordinate")
   df = pd.DataFrame(columns = stations.columns)
   df = extract_wlv_pnt(storm=STORM, datafile1=RUNdir+'/fort.61.nc', stations=stations, df=df)
   #df.to_pickle(RUNdir+"ModelWLV.pkl")
   df.to_csv(RUNdir+"/ModelWLV.csv")


