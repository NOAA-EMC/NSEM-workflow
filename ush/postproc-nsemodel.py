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
# Python script to postprocess NSEM output
#
# -----------------------------------------------------------

import os, sys
import subprocess as sp

# Get enviroment vars from ecFlow scripting
ROOTDIR = os.getenv('ROOTDIR')
NEMSDIR = os.getenv('NEMSDIR')
RUNdir = os.getenv('RUNdir')
PARMnsem = os.getenv('PARMnsem')
FIXnsem = os.getenv('FIXnsem')
EXECnsem = os.getenv('EXECnsem')
COMOUT = os.getenv('COMOUT')
STORM = os.getenv('STORM')
RUN_TYPE = os.getenv('RUN_TYPE')

USHnsem = os.getenv('USHnsem')
sys.path.append(USHnsem)
import nsem_utils
import plot_ww3_unstr
print('Inherited methods:')
print(dir(nsem_utils))
print(dir(plot_ww3_unstr))

# Select appropriate base_info according selected storm
try:
    os.system('rm base_info.pyc'  )
except:
    pass
if 'base_info' in sys.modules:  
    del(sys.modules["base_info"])

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

os.chdir(RUNdir)
print("Executing in", RUNdir)

if (RUN_TYPE == 'tide_spinup') | \
   (RUN_TYPE == 'tide_baserun') | \
   (RUN_TYPE == 'best_track2ocn') | \
   (RUN_TYPE == 'wav&best_track2ocn') | \
   (RUN_TYPE == 'atm2ocn') | \
   (RUN_TYPE == 'wav2ocn') | \
   (RUN_TYPE == 'atm&wav2ocn') | \
   (RUN_TYPE == 'atm2wav2ocn'):
   #--- Process ADCIRC output --- 
   print("Copying the ADCIRC NetCDF files to COMOUT...")
   os.system('cp -p fort.61.nc ${COMOUT}/')  # Elevation Time Series at Specified Elevation Recording Stations
   os.system('cp -p fort.63.nc ${COMOUT}/')  # Elevation Time Series at All Nodes in the Model Grid
   os.system('cp -p fort.64.nc ${COMOUT}/')  # Depth-averaged Velocity Time Series at All Nodes in the Model Grid

if RUN_TYPE == 'atm2wav2ocn':
   #--- Process WW3 output ---
   # Rename the binary output
   os.system('mv out_grd.inlet out_grd.ww3')

   # Populate the postprocessing input template
   print("Postprocessing the WW3 binary output to NetCDF...")
   MESHFILE = sp.getoutput('ls -t *.msh | head -1')
   print('Opening mesh file: '+RUNdir+'/'+MESHFILE)
   f=open(RUNdir+'/'+MESHFILE)
   lines=f.readlines()
   nnodes = lines[4]

   dc_ww3_ounf={}
   dc_ww3_ounf.update({'start_pdy'    :base_info.tide_spin_end_date.strftime("%Y%m%d %H%M%S") })
   dc_ww3_ounf.update({'nnodes'       :nnodes })
   ##
   tmpname = os.path.join(FIXnsem, 'templates', base_info.ww3_ounf_tmpl)
   ww3_ounf = os.path.join(RUNdir,'ww3_ounf.inp')
   nsem_utils.tmp2scr(filename=ww3_ounf,tmpname=tmpname,d=dc_ww3_ounf)

   os.system('${EXECnsem}/ww3_ounf ww3_ounf.inp > ww3_ounf.out')

   # Create field plots of WW3 variables
   print("Creating field plots...") 
   # Wave heights
   DATAFILE = sp.getoutput('ls -t ww3*hs*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE)
   plot_ww3_unstr.plot_hs(storm=STORM, datafile1=DATAFILE) 
   # Peak wave frequency
   DATAFILE = sp.getoutput('ls -t ww3*fp*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE)
   plot_ww3_unstr.plot_fp(storm=STORM, datafile1=DATAFILE)
   # Peak wave direction
   DATAFILE = sp.getoutput('ls -t ww3*dp*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE)
   plot_ww3_unstr.plot_dp(storm=STORM, datafile1=DATAFILE)
   # Water levels
   DATAFILE = sp.getoutput('ls -t ww3*wlv*.nc | head -1')
   DATAFILE2 = sp.getoutput('ls -t ww3*dpt*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE+', '+DATAFILE2)
   plot_ww3_unstr.plot_wlv(storm=STORM, datafile1=DATAFILE, datafile2=DATAFILE2)
   # Currents
   DATAFILE = sp.getoutput('ls -t ww3*cur*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE)
   plot_ww3_unstr.plot_cur(storm=STORM, datafile1=DATAFILE)
   # Wind fields
   DATAFILE = sp.getoutput('ls -t ww3*wnd*.nc | head -1')
   print('Plotting fields for STORM, DATAFILE: '+STORM+', '+DATAFILE)
   plot_ww3_unstr.plot_wnd(storm=STORM, datafile1=DATAFILE)

   os.system('tar -czvf plots_nsem_'+STORM+'.tgz nsem_'+STORM+'*.png')

   # Point outout
   os.system('cp ${FIXnsem}/templates/ww3_ounp.inp ${RUNdir}')
   os.system($NSEMdir/exec/ww3_ounp ww3_ounp.inp > ww3_ounp.out)

   # Move the output to COMOUT
   print("Copying the WW3 NetCDF files to COMOUT...")
   os.system('cp -p ww3.field*.nc ${COMOUT}/')
   print("Moving the WW3 plots to COMOUT...")
   os.system('cp -p plots_nsem_'+STORM+'.tgz ${COMOUT}/')

print("Completed NSEM post.")
