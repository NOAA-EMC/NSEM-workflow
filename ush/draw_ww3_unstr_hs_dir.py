# Script for plotting unstructured WW3 output files in netCDF format, created by ww3_ounf
# Andre van der Westhuysen, 08/21/13
#
import matplotlib
matplotlib.use('Agg',warn=False)

import datetime
from matplotlib.tri import Triangulation, TriAnalyzer, LinearTriInterpolator
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
#from mpl_toolkits.basemap import Basemap

# Set site ID
siteid = 'Shinnecock'

#Get date
now = datetime.datetime.now()
nowstr = str(now)
nowstr = nowstr[0:4]+nowstr[5:7]+nowstr[8:10]

#Single file netCDF reading
#ncf='ww3.20130816_hs.nc'
#nco=netCDF4.Dataset(ncf)

#Multiple file netCDF reading
ncf='ww3.Constant.20080905_hs.nc'
nco=netCDF4.Dataset(ncf)
ncf2='ww3.Constant.20080905_dp.nc'
nco2=netCDF4.Dataset(ncf2)

#Get fields to plot
lon=nco.variables['longitude'][:]
lat=nco.variables['latitude'][:]
timeindays=nco.variables['time'][:]
hs=nco.variables['hs'][:]

timeindays2=nco2.variables['time'][:]
dir=nco2.variables['dp'][:]

reflon=np.linspace(lon.min(),lon.max(),1000)
reflat=np.linspace(lat.min(),lat.max(),1000)
reflon,reflat=np.meshgrid(reflon,reflat)

#Read obs point locations
#data=np.loadtxt('erie_ndbc.loc', comments = '$')
#buoylon=data[:,0]
#buoylat=data[:,1]

plt.figure(figsize = [6.4, 3.8])

#Loop through each time step and plot results
for ind in range(0, len(timeindays)): 
   dt = datetime.datetime.combine(datetime.date(1990, 1, 1), datetime.time(0, 0)) + datetime.timedelta(days=timeindays[ind])
   dstr = datetime.date.strftime(dt,'%Y%m%d%H:%M:%S')
   dstr = dstr[0:8]+' '+dstr[8:17]
   print('Plotting '+dstr)

   par=np.double(hs[ind,:])
   par2=np.double(dir[ind,:])

   flatness=0.10  # flatness is from 0-.5 .5 is equilateral triangle
   tri=Triangulation(lon,lat)
   mask = TriAnalyzer(tri).get_flat_tri_mask(flatness)
   tri.set_mask(mask)

   tli=LinearTriInterpolator(tri,par)
   par_interp=tli(reflon,reflat)
   tli2=LinearTriInterpolator(tri,par2)
   par2_interp=tli2(reflon,reflat)

   #Set up a Mercator projection basemap
   plt.clf()
   #m=Basemap(projection='merc',llcrnrlon=reflon.min(),urcrnrlon=reflon.max(),\
   #    llcrnrlat=reflat.min(),urcrnrlat=reflat.max(),resolution='h')
   #x,y=m(reflon,reflat)
   x = reflon
   y = reflat

   u=np.cos(np.pi/180*(270-par2_interp))
   v=np.sin(np.pi/180*(270-par2_interp))

   plt.pcolormesh(x,y,par_interp,vmax=4.0,shading='flat',cmap=plt.cm.jet)
   plt.colorbar()
   rowskip=np.floor(par2_interp.shape[0]/25)
   colskip=np.floor(par2_interp.shape[1]/25)
   rowskip = 50
   colskip = 50
   plt.quiver(x[0::rowskip,0::colskip],y[0::rowskip,0::colskip],\
         u[0::rowskip,0::colskip],v[0::rowskip,0::colskip], \
         scale = 50, color='black',pivot='middle',units='xy',alpha=0.7)
   plt.xticks(fontsize=9)
   plt.yticks(fontsize=9)

   #m.drawcoastlines()
   #m.fillcontinents()
   #m.drawmeridians(np.arange(int(lon.min()),int(lon.max())+1,1),labels=[0,0,0,1])
   #m.drawparallels(np.arange(int(lat.min()),int(lat.max())+1,0.5),labels=[0.5,0,0,0])
   #m.drawmapboundary()

   figtitle = siteid+': Hsig (m) and Dir: '+dstr
   plt.title(figtitle)

   dtlabel = datetime.date.strftime(dt,'%Y%m%d%H%M%S')
   dtlabel = dtlabel[0:8]+'_'+dtlabel[8:14]
   filenm = nowstr+'_'+siteid+'_hs_dp_'+dtlabel+'.png'
   plt.savefig(filenm,dpi=150,bbox_inches='tight',pad_inches=0.5)

   del(par)




