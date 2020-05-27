import os, sys
from string import Template

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

# Select appropriate base_info according selected storm
try:
    os.system('rm base_info.pyc'  )
except:
    pass
if 'base_info' in sys.modules:  
    del(sys.modules["base_info"])

sys.path.append(PARMnsem+'/storms/'+STORM)
import base_info

##################################
# NOTE: This should be moved to a separate module
def tmp2scr(filename,tmpname,d):
    """
    Replace a pattern in tempelate file and generate a new input file.
    filename: full path to input file
    tmpname:  full path to tempelate file
    d:        dictionary of all patterns need to replace   

    Uses string.Template from the Python standard library
    """
     
    fileout = open( filename,'w' )
    filetmp = open( tmpname ,'r' )
    out     = Template( filetmp.read() ).safe_substitute(d)
    fileout.write(str(out))
    fileout.close()
    filetmp.close()
##################################

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
   print("Moving the ADCIRC NetCDF files to COMOUT...")
   os.system('mv fort.61.nc ${COMOUT}')  # Elevation Time Series at Specified Elevation Recording Stations
   os.system('mv fort.63.nc ${COMOUT}')  # Elevation Time Series at All Nodes in the Model Grid
   os.system('mv fort.64.nc ${COMOUT}')  # Depth-averaged Velocity Time Series at All Nodes in the Model Grid

if RUN_TYPE == 'atm2wav2ocn':
   #--- Process WW3 output ---
   # Rename the binary output
   os.system('mv out_grd.inlet out_grd.ww3')

   # Populate the postprocessing input template
   print("Postprocessing the WW3 binary output to NetCDF...")
   #os.system('MESHFILE=$(ls -t *.msh | head -1')
   #os.system('echo ${MESHFILE}')
   f=open(RUNdir+'/inlet.msh')
   lines=f.readlines()
   nnodes = lines[4]

   dc_ww3_ounf={}
   dc_ww3_ounf.update({'start_pdy'    :base_info.tide_spin_end_date.strftime("%Y%m%d %H%M%S") })
   dc_ww3_ounf.update({'nnodes'       :nnodes })
   ##
   tmpname = os.path.join(FIXnsem, 'templates', base_info.ww3_ounf_tmpl)
   ww3_ounf = os.path.join(RUNdir,'ww3_ounf.inp')
   tmp2scr(filename=ww3_ounf,tmpname=tmpname,d=dc_ww3_ounf)

   os.system('cp ${FIXnsem}/templates/ww3_ounf.inp ${RUNdir}')
   os.system('${EXECnsem}/ww3_ounf ww3_ounf.inp > ww3_ounf.out')

   # Move the output to COMOUT
   print("Moving the WW3 NetCDF files to COMOUT...")
   os.system('mv ww3*.nc ${COMOUT}')

print("Completed NSEM post.")
