# Script for plotting unstructured WW3 output files in netCDF format, created by ww3_ounf
# Andre van der Westhuysen, 09/08/20
#
import matplotlib
matplotlib.use('Agg',warn=False)

import os, sys
import datetime
from matplotlib.tri import Triangulation, TriAnalyzer, LinearTriInterpolator
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import pandas as pd
import cartopy	
import cartopy.crs as ccrs	
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

NSEMdir = os.environ['NSEMdir']
STORM = os.getenv('STORM')
PARMnsem = os.environ['PARMnsem']
cartopy.config['pre_existing_data_dir'] = NSEMdir+'/lib/cartopy'
print('Reading cartopy shapefiles from:')
print(cartopy.config['pre_existing_data_dir'])

# Select appropriate base_info according selected storm
try:
    os.system('rm base_info.pyc'  )
except:
    pass
if 'base_info' in sys.modules:  
    del(sys.modules["base_info"])

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

def plot_wnd(storm, datafile1, datafile2=None):

   #Single file netCDF reading
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)

   #Get fields to plot
   lon=nco.variables['x'][:]
   lat=nco.variables['y'][:]
   timeinsec=nco.variables['time'][:]
   uwnd=nco.variables['windx'][:]
   vwnd=nco.variables['windy'][:]
   triangles=nco.variables['element'][:,:]

   reflon=np.linspace(lon.min(),lon.max(),1000)
   reflat=np.linspace(lat.min(),lat.max(),1000)
   #reflon=np.linspace(-80.40, -74.75, 1000)
   #reflat=np.linspace(32.50, 36.60, 1000)
   #reflon=np.linspace(-75.70, -71.05, 1000)
   #reflat=np.linspace(38.50, 41.40, 1000)
   #reflon=np.linspace(-80.40, -73.35, 1000)
   #reflat=np.linspace(32.50, 39.50, 1000)
   #reflon=np.linspace(-85.30, -78.50, 1000)
   #reflat=np.linspace(23.00, 29.70, 1000)
   reflon,reflat=np.meshgrid(reflon,reflat)

   plt.figure(figsize = [6.4, 3.8])

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   triangles=triangles-1  # Correct indices for Python's zero-base
   tri=Triangulation(lon,lat,triangles=triangles)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   # Loop through each time step and plot results
   for ind in range(0, len(timeinsec)):
      besttrack = pd.read_csv(PARMnsem+'/storms/'+STORM+'/best_track.txt', header=None, skiprows=4, delim_whitespace=True) 
      plt.clf()
      ax = plt.axes(projection=ccrs.Mercator())
      ax.set_extent([-100.00, -50.00, 4.00, 48.00], crs=ccrs.PlateCarree())
      #ax.set_extent([-80.40, -74.75, 32.50, 36.60], crs=ccrs.PlateCarree()) 
      #ax.set_extent([-80.40, -73.35, 32.50, 39.50], crs=ccrs.PlateCarree())  
      #ax.set_extent([-85.30, -78.50, 23.00, 29.70], crs=ccrs.PlateCarree())   

      dt = base_info.tide_spin_start_date + datetime.timedelta(seconds=timeinsec[ind])
      dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
      dstr = dstr[0:8]+' '+dstr[8:17]
      print('Plotting '+dstr)

      par=np.sqrt( np.square(np.double(uwnd[ind,:])) + np.square(np.double(vwnd[ind,:])) )
      tli=LinearTriInterpolator(tri,par)
      par_interp=tli(reflon,reflat)

      plt.pcolormesh(reflon,reflat,par_interp,vmax=60.0,shading='flat',cmap=plt.cm.jet, transform=ccrs.PlateCarree())
      cb = plt.colorbar()
      cb.ax.tick_params(labelsize=8)
      coast = cfeature.GSHHSFeature(scale='high',edgecolor='black',facecolor='none',linewidth=0.25)	
      ax.add_feature(coast)
      plt.plot(besttrack.iloc[:,3].values, besttrack.iloc[:,2].values, 'k--', linewidth=1.0, transform=ccrs.PlateCarree())

      gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
      gl.xlabels_top = False
      gl.ylabels_right = False
      gl.xlines = False
      gl.ylines = False
      gl.xformatter = LONGITUDE_FORMATTER
      gl.yformatter = LATITUDE_FORMATTER
      gl.xlabel_style = {'size': 6, 'color': 'black'}
      gl.ylabel_style = {'size': 6, 'color': 'black'}
      figtitle = storm.capitalize()+': U10 (m/s): '+dstr
      plt.title(figtitle)

      dtlabel = datetime.date.strftime(dt,'%Y%m%d%H%M%S')
      dtlabel = dtlabel[0:8]+'_'+dtlabel[8:14]
      filenm = 'nsem_'+storm+'_wnd_'+dtlabel+'.png'
      plt.savefig(filenm,dpi=150,bbox_inches='tight',pad_inches=0.1)

      del(par)
      del(par_interp)

def plot_dp(storm, datafile1, datafile2=None):

   #Single file netCDF reading
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)

   #Get fields to plot
   lon=nco.variables['longitude'][:]
   lat=nco.variables['latitude'][:]
   timeindays=nco.variables['time'][:]
   dp=nco.variables['dp'][:]
   triangles=nco.variables['tri'][:,:]

   reflon=np.linspace(lon.min(),lon.max(),1000)
   reflat=np.linspace(lat.min(),lat.max(),1000)
   #reflon=np.linspace(-80.40, -73.35, 1000)
   #reflat=np.linspace(32.50, 39.50, 1000)
   reflon,reflat=np.meshgrid(reflon,reflat)

   plt.figure(figsize = [6.4, 3.8])

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   triangles=triangles-1  # Correct indices for Python's zero-base
   tri=Triangulation(lon,lat,triangles=triangles)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   # Loop through each time step and plot results
   for ind in range(0, len(timeindays)): 
      besttrack = pd.read_csv(PARMnsem+'/storms/'+STORM+'/best_track.txt', header=None, skiprows=4, delim_whitespace=True)
      plt.clf()
      ax = plt.axes(projection=ccrs.Mercator())
      ax.set_extent([-100.00, -50.00, 4.00, 48.00], crs=ccrs.PlateCarree())
      #ax.set_extent([-80.40, -73.35, 32.50, 39.50], crs=ccrs.PlateCarree())     

      dt = datetime.datetime.combine(datetime.date(1990, 1, 1), datetime.time(0, 0)) + datetime.timedelta(days=timeindays[ind])
      dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
      dstr = dstr[0:8]+' '+dstr[8:17]
      print('Plotting '+dstr)

      par=np.double(dp[ind,:])
      tli=LinearTriInterpolator(tri,par)
      par_interp=tli(reflon,reflat)

      plt.pcolormesh(reflon,reflat,par_interp,vmin=0.0,vmax=360.0,shading='flat',cmap=plt.cm.jet, transform=ccrs.PlateCarree())
      cb = plt.colorbar()
      cb.ax.tick_params(labelsize=8)
      coast = cfeature.GSHHSFeature(scale='high',edgecolor='black',facecolor='none',linewidth=0.25)	
      ax.add_feature(coast)
      plt.plot(besttrack.iloc[:,3].values, besttrack.iloc[:,2].values, 'k--', linewidth=1.0, transform=ccrs.PlateCarree())

      gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
      gl.xlabels_top = False
      gl.ylabels_right = False
      gl.xlines = False
      gl.ylines = False
      gl.xformatter = LONGITUDE_FORMATTER
      gl.yformatter = LATITUDE_FORMATTER
      gl.xlabel_style = {'size': 6, 'color': 'black'}
      gl.ylabel_style = {'size': 6, 'color': 'black'}
      figtitle = storm.capitalize()+': Peak Dir (deg): '+dstr
      plt.title(figtitle)

      dtlabel = datetime.date.strftime(dt,'%Y%m%d%H%M%S')
      dtlabel = dtlabel[0:8]+'_'+dtlabel[8:14]
      filenm = 'nsem_'+storm+'_dp_'+dtlabel+'.png'
      plt.savefig(filenm,dpi=150,bbox_inches='tight',pad_inches=0.1)

      del(par)
      del(par_interp)

def plot_wlv(storm, datafile1, datafile2=None):

   #Single file netCDF reading
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)
   ncf2=datafile2
   nco2=netCDF4.Dataset(ncf2)

   #Get fields to plot
   lon=nco.variables['x'][:]
   lat=nco.variables['y'][:]
   timeinsec=nco.variables['time'][:]
   #base_date=nco.variables['time:base_date']
   #print(base_date)
   wlv=nco.variables['zeta'][:]
   triangles=nco.variables['element'][:,:]

   #AW dpt=nco2.variables['dpt'][:]

   reflon=np.linspace(lon.min(),lon.max(),1000)
   reflat=np.linspace(lat.min(),lat.max(),1000)
   #reflon=np.linspace(-80.40, -74.75, 1000)
   #reflat=np.linspace(32.50, 36.60, 1000)
   #reflon=np.linspace(-80.40, -73.35, 1000)
   #reflat=np.linspace(32.50, 39.50, 1000)
   #reflon=np.linspace(-85.30, -78.50, 1000)
   #reflat=np.linspace(23.00, 29.70, 1000)
   reflon,reflat=np.meshgrid(reflon,reflat)

   plt.figure(figsize = [6.4, 3.8])

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   triangles=triangles-1  # Correct indices for Python's zero-base
   tri=Triangulation(lon,lat,triangles=triangles)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   # Loop through each time step and plot results
   for ind in range(0, len(timeinsec)):
      besttrack = pd.read_csv(PARMnsem+'/storms/'+STORM+'/best_track.txt', header=None, skiprows=4, delim_whitespace=True) 
      plt.clf()
      ax = plt.axes(projection=ccrs.Mercator())
      ax.set_extent([-100.00, -50.00, 4.00, 48.00], crs=ccrs.PlateCarree())
      #ax.set_extent([-80.40, -74.75, 32.50, 36.60], crs=ccrs.PlateCarree())
      #ax.set_extent([-80.40, -73.35, 32.50, 39.50], crs=ccrs.PlateCarree())
      #ax.set_extent([-85.30, -78.50, 23.00, 29.70], crs=ccrs.PlateCarree()) 
 
      dt = base_info.tide_spin_start_date + datetime.timedelta(seconds=timeinsec[ind])
      dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
      dstr = dstr[0:8]+' '+dstr[8:17]
      print('Plotting '+dstr)

      par=np.double(wlv[ind,:])
      tli=LinearTriInterpolator(tri,par)
      par_interp=tli(reflon,reflat)

      plt.pcolormesh(reflon,reflat,par_interp,vmin=-2.0,vmax=2.0, shading='flat',cmap=plt.cm.bwr, transform=ccrs.PlateCarree())
      cb = plt.colorbar()
      cb.ax.tick_params(labelsize=8)
      coast = cfeature.GSHHSFeature(scale='high',edgecolor='black',facecolor='none',linewidth=0.25)	
      ax.add_feature(coast)
      plt.plot(besttrack.iloc[:,3].values, besttrack.iloc[:,2].values, 'k--', linewidth=1.0, transform=ccrs.PlateCarree())

      gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
      gl.xlabels_top = False
      gl.ylabels_right = False
      gl.xlines = False
      gl.ylines = False
      gl.xformatter = LONGITUDE_FORMATTER
      gl.yformatter = LATITUDE_FORMATTER
      gl.xlabel_style = {'size': 6, 'color': 'black'}
      gl.ylabel_style = {'size': 6, 'color': 'black'}
      figtitle = storm.capitalize()+': WL (m MSL): '+dstr
      plt.title(figtitle)

      dtlabel = datetime.date.strftime(dt,'%Y%m%d%H%M%S')
      dtlabel = dtlabel[0:8]+'_'+dtlabel[8:14]
      filenm = 'nsem_'+storm+'_wlv_'+dtlabel+'.png'
      plt.savefig(filenm,dpi=150,bbox_inches='tight',pad_inches=0.1)

      del(par)
      del(par_interp)

def plot_cur(storm, datafile1, datafile2=None):

   #Single file netCDF reading
   ncf=datafile1
   nco=netCDF4.Dataset(ncf)
   #ncf2=datafile2
   #nco2=netCDF4.Dataset(ncf2)

   #Get fields to plot
   lon=nco.variables['longitude'][:]
   lat=nco.variables['latitude'][:]
   timeindays=nco.variables['time'][:]
   ucur=nco.variables['ucur'][:]
   vcur=nco.variables['vcur'][:]
   triangles=nco.variables['tri'][:,:]

   #timeindays2=nco2.variables['time'][:]
   #dir=nco2.variables['dp'][:]

   reflon=np.linspace(lon.min(),lon.max(),1000)
   reflat=np.linspace(lat.min(),lat.max(),1000)
   #reflon=np.linspace(-80.40, -73.35, 1000)
   #reflat=np.linspace(32.50, 39.50, 1000)
   reflon,reflat=np.meshgrid(reflon,reflat)

   plt.figure(figsize = [6.4, 3.8])

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   triangles=triangles-1  # Correct indices for Python's zero-base
   tri=Triangulation(lon,lat,triangles=triangles)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   # Loop through each time step and plot results
   for ind in range(0, len(timeindays)): 
      besttrack = pd.read_csv(PARMnsem+'/storms/'+STORM+'/best_track.txt', header=None, skiprows=4, delim_whitespace=True)
      plt.clf()
      ax = plt.axes(projection=ccrs.Mercator())
      ax.set_extent([-100.00, -50.00, 4.00, 48.00], crs=ccrs.PlateCarree())
      #ax.set_extent([-80.40, -73.35, 32.50, 39.50], crs=ccrs.PlateCarree())     

      dt = base_info.tide_spin_start_date + datetime.timedelta(days=timeindays[ind])
      dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
      dstr = dstr[0:8]+' '+dstr[8:17]
      print('Plotting '+dstr)

      par=np.sqrt( np.square(np.double(ucur[ind,:])) + np.square(np.double(vcur[ind,:])) )
      #par2=np.double(dir[ind,:])

      tli=LinearTriInterpolator(tri,par)
      par_interp=tli(reflon,reflat)

      #u=np.cos(np.pi/180*(270-par_interp))
      #v=np.sin(np.pi/180*(270-par_interp))

      plt.pcolormesh(reflon,reflat,par_interp,vmin=0.0,vmax=2.0,shading='flat',cmap=plt.cm.jet, transform=ccrs.PlateCarree())
      #plt.contourf(reflon, reflat, par_interp, vmax=60.0, cmap=plt.cm.jet, transform=ccrs.PlateCarree())
      cb = plt.colorbar()
      cb.ax.tick_params(labelsize=8)
      #rowskip=np.floor(par_interp.shape[0]/25)
      #colskip=np.floor(par_interp.shape[1]/25)
      rowskip = 50
      colskip = 50
      #plt.quiver(reflon[0::rowskip,0::colskip],reflat[0::rowskip,0::colskip],\
      #      u[0::rowskip,0::colskip],v[0::rowskip,0::colskip], \
      #      scale = 50, color='black',pivot='middle',units='xy',alpha=0.7)
      coast = cfeature.GSHHSFeature(scale='high',edgecolor='black',facecolor='none',linewidth=0.25)	
      ax.add_feature(coast)
      plt.plot(besttrack.iloc[:,3].values, besttrack.iloc[:,2].values, 'k--', linewidth=1.0, transform=ccrs.PlateCarree())

      gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
      gl.xlabels_top = False
      gl.ylabels_right = False
      gl.xlines = False
      gl.ylines = False
      gl.xformatter = LONGITUDE_FORMATTER
      gl.yformatter = LATITUDE_FORMATTER
      gl.xlabel_style = {'size': 6, 'color': 'black'}
      gl.ylabel_style = {'size': 6, 'color': 'black'}
      figtitle = storm.capitalize()+': Cur (m/s): '+dstr
      plt.title(figtitle)

      dtlabel = datetime.date.strftime(dt,'%Y%m%d%H%M%S')
      dtlabel = dtlabel[0:8]+'_'+dtlabel[8:14]
      filenm = 'nsem_'+storm+'_cur_'+dtlabel+'.png'
      plt.savefig(filenm,dpi=150,bbox_inches='tight',pad_inches=0.1)

      del(par)
      del(par_interp)

if __name__ == "__main__":
   plot_wnd(storm='shinnecock', datafile1='ww3.field.2008_wnd.nc')

