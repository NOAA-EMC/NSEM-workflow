# To Use - import this into your python script as follow:
# import nsem_env

import sys, os


RUNdir = os.getenv('RUNdir')
PRJdir = os.getenv('NWROOT')
EXECnsem = os.getenv('EXECnsem')
PARMnsem = os.getenv('PARMnsem')
FIXnsem = os.getenv('FIXnsem')
USHnsem = os.getenv('USHnsem')
GESIN = os.getenv('GESIN')
COMIN = os.getenv('COMIN')
COMINatm = os.getenv('COMINatm')
COMINwave = os.getenv('COMINww3')
COMINwavdata = os.getenv('COMINww3data')
COMINadc = os.getenv('COMINadc')
jlogfile = os.getenv('jlogfile')

storm = os.getenv('STORM')
run = os.getenv('RUN_TYPE')

start_date_str = "04/09/2008 12:00:00"
frcst_hrs = 36

if storm:
    pass
else:
    print("\nEnvironment is not set! Please source 'nsem_export.sh' file and re run the program\n")
    sys.exit(-1)

sys.path.append(USHnsem)

print("\n")
print("Logfile: /scratch2/COASTAL/coastal/scrub/com/nsem/para/logs/jlogfile.tide_spinup")
print("\n")

