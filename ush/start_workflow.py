#!/usr/bin/env python


# standard libs
import glob, os, sys, re, time, argparse
import datetime, subprocess
from importlib import import_module
"""
result = getattr(foo, 'bar')()
class A:
    def __init__(self):
        pass

    def sampleFunc(self, arg):
        print('you called sampleFunc({})'.format(arg))

m = globals()['A']()
func = getattr(m, 'sampleFunc')
func('sample arg')

# Sample, all on one line
getattr(globals()['A'](), 'sampleFunc')('sample arg')
And, if not a class:

def sampleFunc(arg):
    print('you called sampleFunc({})'.format(arg))

globals()['sampleFunc']('sample arg')

import importlib
function_string = 'mypackage.mymodule.myfunc'
mod_name, func_name = function_string.rsplit('.',1)
mod = importlib.import_module(mod_name)
func = getattr(mod, func_name)
result = func()


# add this
import logging
logger = logging.getLogger('ftpuploader')
hdlr = logging.FileHandler('ftplog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

"""

from pathlib import Path

# local libs
from color import Color, Formatting, Base, ANSI_Compatible


# globals - updated during reading command line
PRJ_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent 
RUN_DIR = os.path.dirname(os.path.abspath(__file__))


def now(frmt=1):

    now = datetime.datetime.now()

    if frmt == 1:
        now = now.strftime("%Y-%m-%d %H:%M:%S")
    elif frmt == 2:
        now = now.strftime("%b. %d, %Y")
    elif frmt == 3:
        now = now.ctime()
    elif frmt == 4:
        now = now.strftime("%Y%m%d")

    return now


def exist(path):
    p = os.path.abspath(path)
    if os.path.isdir(p):
        return 1
    return 0


def found(file):

    f = os.path.abspath(file)
    if not os.path.isfile(f):
        msg = Color.F_Red + "\nFile {} not found!\n".format(file) 
        msg += Color.F_Default
        print(msg)
        return 0
    return 1



# ecflow nco variables:
# **********************
# envir Set to "test" during the initial testing phase, "para" when running in parallel (on a schedule), and "prod" in production. 
# COMROOT com root directory for input/output data on current system ecFlow $COMROOT/$NET/$envir/$RUN.$PDY
# NWROOT Root directory for application, typically /nw$envir 
# GESROOT nwges root directory for input/output guess fields on current system 
# job Unique job name (unique per day and environment) 
# jobid Unique job identifier, typically $job.$$ (where $$ is an ID number) 
# jlogfile Log file for start time, end time, and error messages of all jobs  
# cyc Cycle time in GMT, formatted HH  
# DATAROOT Directory containing the working directory, often /tmpnwprd1 in production 
# HOMEmodel Application home directory, typically $NWROOT/ model.v X . Y . Z 
# SENDWEB Boolean variable used to control sending products to a web server, often ncorzdm 
# KEEPDATA Boolean variable used to specify whether or not the working directory should be deleted upon successful job completion. 

# model_ver Current version of the model; where model is the model's directory name (e.g. for $NWROOT/gfs.v12.0.0, gfs_ver=v12.0.0) 
# jjob nco variables:
# *******************
# pgmout File where stdout of binary executables may be written 
# NET Model name (first level of com directory structure) 
# RUN Name of model run (third level of com directory structure) 
# PDY Date in YYYYMMDD format
# PDYm1-7 Dates of previous seven days in YYYYMMDD format ($PDYm1 is yesterday's date, etc.)  
# PDYp1-7 Dates of next seven days in YYYYMMDD format ($PDYp1 is tomorrow's date, etc.)  
# cycle Cycle time in GMT, formatted tHHz 
# DATA Location of the job working directory, typically $DATAROOT/$jobid  
# USHmodel Location of the model's ush files, typically $HOME model /ush 
# EXECmodel Location of the model's exec files, typically $HOME model /exec 
# PARMmodel Location of the model's parm files, typically $HOME model /parm 
# FIXmodel Location of the model's fix files, typically $HOME model /fix 
# COMIN com directory for current model's input data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
# COMOUT com directory for current model's output data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
# COMINmodel com directory for incoming data from model model 
# COMOUTmodel com directory for outgoing data for model model 
# GESIN nwges directory for input guess fields; typically $GESROOT/$envir
# GESOUT nwges directory for output guess fields; typically $GESROOT/$envir 

# Each job in ecFlow is associated with an ecFlow script which acts like an LSF submission script, 
# 1) setting up the bsub parameters and much of 
# 2) the execution environment and 
# 3) calling the J-job to execute the job.  
# 4) All jobs must be submitted to LSF via bsub . 
# 5) It is at the ecFlow (NCO) or submission script level (development organizations) where certain 
#    environment specific variables must be set

# The purpose of the J-Job is fourfold: 
# 1) to set up location (application/data directory) variables, 
# 2) to set up temporal (date/cycle) variables, 
# 3) to initialize the data and working directories, 
# 4) and to call the ex-script. 

# The ex-script is the driver for the bulk of the application, 
# 1) including data-staging in the working directory, 
# 2) setting up any model-specific variables, 
# 3) moving data to long-term storage, 
# 4) sending products off WCOSS via DBNet and 
# 5) performing appropriate validation and error checking.  
# 6) It may call one or more utility (ush) scripts.
class NCOSystem():

    SCRIPT = 'scripts'
    SOURCE = 'sorc'
    ECF = 'ecf'
    USH = 'ush'
    EXEC = 'exec'
    PARM = 'parm'
    FIX = 'fix'
    JOBS = 'jobs'

    # unique run_dir is constructed by this format
    
    """ $COMROOT/$NET/$envir/$RUN.$PDY
        COMIN com directory for current model's input data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
        COMOUT com directory for current model's output data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
        COMINmodel com directory for incoming data from model model 

    <RUN_DIR>/                                              ==> ${COMROOT}/
        |--- nsem                                           ==> $NET - first level dir
                |--- $envir/                                ==> test|para|prod 
                        |--- logs
                        |     |--- j<logfile>jobid          ==> j$job$$
                        |--- <storm>/                       ==> this is extra in the hi-er-archy
                               |--- <input_data>            ==> $COMIN
                               |     
                               |
                               |--- <run_name>/             ==> $RUN - third level dir
                                        |--- <out_data>/    ==> $COMOUT

                                                            (i.e. $COMROOT/$NET/$envir/$RUN.$PDY 
    'COMROOT' : RUN_DIR,     # let's call this run_dir
    'GESROOT' : GESROOT,     # let's have this in comroot/nwges
    'DATAROOT': DATAROOT,    # let's mak this on /tmp<storm>|/tmp<nsem>
    'NWROOT'  : PRJ_DIR      # let's call this prj_dir

    """
    def __init__(self, event, envir, run_name, dataroot, gesroot, model="nsem"):

        self.COMROOT = RUN_DIR               # COMROOT root directory for input/output data on current system
        self.GESROOT = gesroot               # GESROOT nwges root directory for input/output guess fields on current system
        self.DATAROOT = dataroot             # DATAROOT Directory containing the working directory, often /tmpnwprd1 in production
        self.NWROOT = PRJ_DIR                # NWROOT Root directory for application, typically /nw$envir 
        self.NET = event.lower()
        self.envir = envir.lower()
        self.RUN = run_name.lower()
        self.job = self.RUN                  # job Unique job name (unique per day and environment) 


        self.jlogfile = os.path.join(self.COMROOT, self.envir, "logs", "jlogfile." + self.job)

        # com directory for current model's input data, typically $COMROOT/$NET/$envir/$RUN.$PDY
        self.COMIN = os.path.join(self.COMROOT, self.envir, self.NET)
        
        # com directory for current model's output data, typically $COMROOT/$NET/$envir/$RUN.$PDY
        # see if needed, created in jjob too
        self.COMOUT = os.path.join(self.COMROOT, self.envir, self.NET, self.RUN)

        # GESIN nwges directory for input guess fields; typically $GESROOT/$envir
        self.GESIN = os.path.join(self.GESROOT,self.envir, self.NET, self.RUN)
 
        # GESOUT nwges directory for output guess fields; typically $GESROOT/$envir TODO - see if needed, created in jjob script too
        self.GESOUT = os.path.join(self.GESROOT, self.envir)

        # DATA Location of the job working directory, typically $DATAROOT/$jobid
        # This directory gets created though jjob script, I think make DATAROOT+=NET 


    def write_helper(self, nems_cfg):

        # create a helper export variables 

        nwroot = self.NWROOT

        lines="""#!/bin/sh -l

# To Run: source export_env.sh

# Enviroment vars from ecFlow scripting
export RUN_DIR={}
export NWROOT={}
export FIXnsem={}/fix
export EXECnsem={}/exec
export SORCnsem={}/sorc
export PARMnsem={}/parm
export USHnsem={}/ush
export GESIN={}
export COMIN={}
export COMINatm={}
export COMINwave={}
export COMINwavedata={}
export COMINmeshdata={}
export COMINadc={}
export COMINnwm={}
export STORM={}
export RUN_TYPE={}
export jlogfile={}
""".format(self.COMROOT,nwroot,nwroot,nwroot,nwroot,nwroot,nwroot,self.GESIN,self.COMIN,
           os.path.join(self.COMIN,"atm"), os.path.join(self.COMIN,"ww3"),
           os.path.join(self.COMIN,"ww3data"), os.path.join(self.COMIN,"atmesh"),
           os.path.join(self.COMIN,"adcirc"), os.path.join(self.COMIN,"nwm"),
           self.NET, self.RUN, self.jlogfile)

        outfile = os.path.join(self.ush_dir(), "nsem_export.sh")
        with open(outfile, 'w') as fptr:
            fptr.write(lines)

        # change mode
        subprocess.call(["chmod", "a+x", outfile])
       
        print("\nProcessed helper export script %s" %outfile)
        
        start_date, start_date_str = nems_cfg.get_duration()

        lines= "# To Use - import this into your python script as follow:\n"
        lines += "# import nsem_env\n"
        lines += "\n"
        lines += "import sys, os\n"
        lines += "\n"
        lines += "\n"
        lines += "RUNdir = os.getenv('RUNdir')\n"
        lines += "PRJdir = os.getenv('NWROOT')\n"
        lines += "EXECnsem = os.getenv('EXECnsem')\n"
        lines += "PARMnsem = os.getenv('PARMnsem')\n"
        lines += "FIXnsem = os.getenv('FIXnsem')\n"
        lines += "USHnsem = os.getenv('USHnsem')\n"
        lines += "GESIN = os.getenv('GESIN')\n"
        lines += "COMIN = os.getenv('COMIN')\n"
        lines += "COMINatm = os.getenv('COMINatm')\n"
        lines += "COMINwave = os.getenv('COMINww3')\n"
        lines += "COMINwavdata = os.getenv('COMINww3data')\n"
        lines += "COMINadc = os.getenv('COMINadc')\n"
        lines += "jlogfile = os.getenv('jlogfile')\n"
        lines += "\n"
        lines += "storm = os.getenv('STORM')\n"
        lines += "run = os.getenv('RUN_TYPE')\n"
        lines += "\n"
        lines += 'start_date_str = "' + start_date_str + '"\n'
        lines += "frcst_hrs = " + str(nems_cfg.get_fcst_hours()) + "\n"
        lines += "\n"
        lines += "if storm:\n"
        lines += "    pass\n"
        lines += "else:\n"
        lines += '    print("\\nEnvironment is not set! Please source \'nsem_export.sh\' file and re run the program\\n")\n'
        lines += "    sys.exit(-1)\n"
        lines += "\n"
        lines += "sys.path.append(USHnsem)\n"
        lines += "\n"
        lines += 'print("\\n")\n'
        lines += 'print("Logfile: ' + self.jlogfile + '")\n'
        lines += 'print("\\n")\n'
        lines += "\n"

        outfile = os.path.join(self.ush_dir(), "nsem_env.py")
        with open(outfile, 'w') as fptr:
            fptr.write(lines)

        # change mode
        subprocess.call(["chmod", "a+x", outfile])
       
        print("\nProcessed helper environment script %s" %outfile)


    def prj_dir(self):
        dir_iterable = [self.source_dir(), self.script_dir(), self.ecf_dir(), self.parm_dir(),
                        self.fix_dir(), self.ush_dir(), self.exec_dir(), self.jjob_dir(), self.jlogfile]
        # generator expression
        return (dir for dir in dir_iterable)
    
 
    """
    To test in python env:
    >>> get_genrator = self.prj_subdir()
    >>> get_generator
    <generator object prj_subdir at 0x7f78b2e7e2b0>
    >>> line = next(get_generator)
    .../parm/storms/<shinnecock>
    >>> line
    .../fix/meshes/<shinnecock>
    """
    def prj_subdir(self):
        # <prj_dir>/parm/storms/<event> - to exists
        # <prj_dir>/fix/template   
        # <prj_dir>/fix/meshes/<event>   
        # <prj_dir>/sorce/hsofs  hsofs_elevated20m ??
        subdir_iterable = [os.path.join(self.parm_dir(), "storms", self.NET),
                           os.path.join(self.fix_dir(), "meshes", self.NET),
                           os.path.join(self.fix_dir(), "templates")]
        for subdir in subdir_iterable:
            yield subdir


    def source_dir(self):
        return os.path.join(self.NWROOT, self.SOURCE) 


    def script_dir(self):
        return os.path.join(self.NWROOT, self.SCRIPT) 


    def ecf_dir(self):
        return os.path.join(self.NWROOT, self.ECF) 


    def fix_dir(self):
        return os.path.join(self.NWROOT, self.FIX)

 
    def ush_dir(self):
        return os.path.join(self.NWROOT, self.USH)


    def exec_dir(self):
        return os.path.join(self.NWROOT, self.EXEC)


    def parm_dir(self):
        return os.path.join(self.NWROOT, self.PARM)

 
    def jjob_dir(self):
        return os.path.join(self.NWROOT, self.JOBS) 


    def storm_dir(self, which):
        # running two storms even for testing overrides ecf/jjob files! 
        if which == "ecf":
            which = self.ecf_dir()
        elif which == "job":
            which = self.jjob_dir()

        p = os.path.join(which, self.NET)
        if not exist(p):
            print("\nCreating directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
            except subprocess.CalledProcessError as err:
                print('Error in creating directory: ', err)
        return p


    def setup_prjdir(self):
        # update the prj_dir for new storm event - TOO
        # <prj_dir>/parm/<event> - to exists
        # <prj_dir>/fix/meshes/<event>   hsofs  hsofs_elevated20m ??
        # <prj_dir>/sorc/runupforecast.fd ??
        p = self.NWROOT
        if not exist(p):
            print("\nCreating model home directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
                subprocess.check_call(['mkdir', '-v', self.SOURCE, self.SCRIPT, self.ECF, self.FIX, 
                                       self.USH, self.EXEC, self.PARM, self.JOBS], cwd=p)
            except subprocess.CalledProcessError as err:
                print('Error in creating model home directory: ', err)
        else:
            print("\nChecking health of model home directory: {}".format(p))
            for dir in self.prj_dir():
                if not exist(dir):
                    try:
                      subprocess.run(['mkdir', '-vp', dir ], check=True)
                    except subprocess.CalledProcessError as err:
                      print('Error in creating %s directory: ' %(dir, err))
                else:
                    print("\n%s is healthy" %dir) 
  
        # now check on subdirs:    
        print("\nChecking health of model home subdirectories")
        for dir in self.prj_subdir():
            if not exist(dir):
                try:
                  subprocess.run(['mkdir', '-vp', dir ], check=True)
                except subprocess.CalledProcessError as err:
                  print('Error in creating %s directory: ' %(dir, err))
            else:
                print("\n%s is healthy" %dir) 
       


    def setup_rundir(self):
        p = self.COMIN
        if not exist(p):
            print("\nCreating model input directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
                subprocess.check_call(['mkdir', '-v', 'nwm', 'adcirc', 'ww3', 'atmesh', 'atm'], cwd=p)
            except subprocess.CalledProcessError as err:
                print('Error in creating model input directory: ', err)

        """created on script side with id
        p = self.COMOUT   
        if not exist(p):
            print("\nCreating model output directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
            except subprocess.CalledProcessError as err:
                print('Error in creating model input directory: ', err)
        """

        p = self.GESIN
        if not exist(p):
            print("\nCreating gesin directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
            except subprocess.CalledProcessError as err:
                print('Error in creating gesin directory: ', err)

        """created on script side with id
        p = self.GESOUT
        if not exist(p):
            print("\nCreating gesout directory: {}".format(p))
            try:
                subprocess.run(['mkdir', '-pv', p ], check=True)
            except subprocess.CalledProcessError as err:
                print('Error in creating gesout directory: ', err)
       """ 


    def write_ecf2(self, slurm):

        sbatch_part = slurm.get_sbatch()

        lines = """\n\n#%include <head.h>
#%include <envir.h> 

# base name of model directory (i.e. storm)
export model={}          

# set to test during the initial testing phase, para when running 
# in parallel (on a schedule), and prod in production
export envir={}

export DEVWCOSS_USER=$(whoami)

# models input/output location
export COMROOT={}

# models restart/spinup files location
export GESROOT={}

# root directory for application, typically /nw$envir 
export NWROOT={}

# unique job name (unique per day and environment), run_name
export job=j{}
export jobid=$job.$$

# temp directory containing the working directory, often /tmpnwprd1 in production 
export DATAROOT={}
   

# dev environment jlogfile
mkdir -p ${{COMROOT}}/logs/${{envir}}
export jlogfile=${{COMROOT}}/logs/${{envir}}/jlogfile.${{job}}

# call the jjob script
${{NWROOT}}/jobs/{}


#%manual
######################################################################
# Task script:     j{}
# Last modifier:   Andre van der Westhuysen
# Organization:    NOAA/NCEP/EMC/NOS/OWP
# Date:            {}
# Purpose: To execute the job for ADC-WW3-NWM model
######################################################################
######################################################################
# Job specific troubleshooting instructions:
# see generic troubleshoot manual page
#
######################################################################
#%end""".format(self.NET, self.envir, self.COMROOT, self.GESROOT,
                self.NWROOT, self.RUN, self.DATAROOT,
                "J"+self.RUN.upper(),
                self.RUN, now(2))

        outfile = os.path.join(self.ecf_dir(), "j"+self.RUN + ".ecf")
        # running two storms at once, even for testing, overrides ecf files
        # p = self.storm_dir("ecf")
        # outfile = os.path.join(p, "j"+self.RUN + ".ecf")
        with open(outfile, 'w') as fptr:
            fptr.write(sbatch_part+lines)

        # change mode
        subprocess.call(["chmod", "a+x", outfile])

        print("\nProcessed ecflow script %s" %outfile)



    def write_ecf(self, slurm):

        sbatch_part = slurm.get_sbatch()
        
        lines = """\n\n#%include <head.h>
#%include <envir.h> 

# base name of model directory (i.e. storm)
export model={}          

# set to test during the initial testing phase, para when running 
# in parallel (on a schedule), and prod in production
export envir={}

export DEVWCOSS_USER=$(whoami)

# models input/output location
export COMROOT={}

# models restart/spinup files location
export GESROOT={}

# root directory for application, typically /nw$envir 
export NWROOT={}

# unique job name (unique per day and environment), run_name
export job=j{}
export jobid=$job.$$

# temp directory containing the working directory, often /tmpnwprd1 in production 
export DATAROOT={}

# log directory and files
mkdir -p {}
export jlogfile={}

# call the jjob script
{}


#%manual
######################################################################
# Task script:     j{}
# Last modifier:   Andre van der Westhuysen
# Organization:    NOAA/NCEP/EMC/NOS/OWP
# Date:            {}
# Purpose: To execute the job for ADC-WW3-NWM model
######################################################################
######################################################################
# Job specific troubleshooting instructions:
# see generic troubleshoot manual page
#
######################################################################
#%end""".format(self.NET, self.envir, self.COMROOT, self.GESROOT,
                self.NWROOT, self.RUN, self.DATAROOT, 
                os.path.join(self.COMROOT, self.envir, "logs"),
                self.jlogfile,
                os.path.join(self.jjob_dir(),"J"+self.RUN.upper()), 
                self.RUN, now(2))

        outfile = os.path.join(self.ecf_dir(), "j"+self.RUN + ".ecf")
        # running two storms at once, even for testing, overrides ecf files
        # p = self.storm_dir("ecf")
        # outfile = os.path.join(p, "j"+self.RUN + ".ecf")
        with open(outfile, 'w') as fptr:
            fptr.write(sbatch_part+lines)

        # change mode
        subprocess.call(["chmod", "a+x", outfile])

        print("\nProcessed ecflow script %s" %outfile)




    def write_jjob(self):
    
        lines="""#!/bin/sh 
 
date
export PS4=' $SECONDS + ' 
set -x 
 
export pgm="NWPS"
export pgmout=OUTPUT.$$
 
export KEEPDATA="YES"     # TODO - to see

PDY={}

# temp location of the job working directory, typically $DATAROOT/$jobid 
export DATA=${{DATA:-${{DATAROOT:?}}/$jobid}}
mkdir -p $DATA   
cd $DATA

####################################
# Specify NET and RUN Name and model
####################################
export NET={}
#export RUN=$(echo j{}|awk -F"_" '{{print $2}}')

####################################
# SENDECF  - Flag Events on ECFLOW
# SENDCOM  - Copy Files From TMPDIR to $COMOUT
# SENDDBN  - Issue DBNet Client Calls
####################################
export SENDCOM=${{SENDCOM:-YES}}
export SENDECF=${{SENDECF:-YES}}
export SENDDBN=${{SENDDBN:-NO}}

# Specify Execution Areas
####################################
export HOMEnsem={}
export FIXnsem={}
export EXECnsem={}
export SORCnsem={}
export PARMnsem={}
export USHnsem={}

# Set processing DIRs here
export INPUTdir=${{INPUTdir:-${{DATA}}/input}}
export RUNdir=${{RUNdir:-${{DATA}}/run}}
export TMPdir=${{TMPdir:-${{DATA}}/tmp}}
export LOGdir=${{LOGdir:-${{DATA}}/logs}}

# Set NWPS run conditions
export DEBUGGING=${{DEBUGGING:-TRUE}}
export DEBUG_LEVEL=${{DEBUG_LEVEL:-1}}
export ISPRODUCTION=${{ISPRODUCTION:-TRUE}}
export SITETYPE=${{SITETYPE:-EMC}}

##############################################
# Define COM directory
##############################################
# com directory for current model's output data, typically $COMROOT/$NET/$envir/$RUN.$PDY
export COMOUT={}
# nwges directory for output guess fields; typically $GESROOT/$envir
export GESOUT={}
# nwges directory for input guess fields; typically $GESROOT/$envir
export GESIN={}

# loop over nems.configure per model(alias), also must match run_name
# COMIN com directory for current model's input data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
# COMINmodel com directory for incoming data from model model 
export COMINatm={}
export COMINwave={}
export COMINwavedata={}
export COMINadc={}
export COMINmeshdata={}
export COMINnwm={}

# check if we need to create COMOUT and GESOUT here or in main?
mkdir -p $INPUTdir $RUNdir $TMPdir $LOGdir $COMOUT $GESOUT
##############################################
# Execute the script
{}
##############################################

#startmsg
msg="JOB j{} HAS COMPLETED NORMALLY."
# postmsg $jlogfile "$msg"

if [ -e $pgmout ]; then
    cat $pgmout
fi

cd {}

if [ "$KEEPDATA" != YES ]; then
    rm -rf $DATA
fi

date

""".format(now(4), self.NET, self.job, self.NWROOT, self.fix_dir(), self.exec_dir(),
           self.source_dir(), self.parm_dir(), self.ush_dir(),
	   self.COMOUT, self.GESOUT, self.GESIN, 
           os.path.join(self.COMIN,"atm"),
	   os.path.join(self.COMIN,"ww3"), os.path.join(self.COMIN,"ww3data"),
	   os.path.join(self.COMIN,"adcirc"), os.path.join(self.COMIN,"atmesh"), 
	   os.path.join(self.COMIN,"nwm"), os.path.join(self.script_dir(),"ex"+self.RUN+".sh"), 
           self.job, self.DATAROOT)
 
        outfile = os.path.join(self.jjob_dir(), "J"+self.RUN.upper())
        # running two storms at once, even for testing, overrides ecf files
        # p = self.storm_dir("job")
        # outfile = os.path.join(p, "J"+self.RUN.upper())
        with open(outfile, 'w') as fptr:
            fptr.write(lines)   

        # change mode
        subprocess.call(["chmod", "a+x", outfile])

        print("\nProcessed ecflow jjob script %s" %outfile)


        # create the script at the same time as jjob
        out = os.path.join(self.script_dir(),"ex"+self.RUN+".sh")

        # this script must exists that does the real work
        p = os.path.join(self.ush_dir(), self.RUN+".py")
        if not found(p):
            print("Warrning - make sure to prepare the script!")

        lines="""
echo "============================================================="
echo "=                                                            "
echo "=         RUNNING NSEM FOR STORM: {}                        
echo "=         RUN NAME: {}                              
echo "=                                                            "
echo "============================================================="
#
python ${{USHnsem}}/{} 

echo "{} completed"
exit 0
""".format(self.NET, self.RUN, self.RUN+".py", self.RUN)
        
        with open(out, 'w') as fptr:
            fptr.write(lines)

        # change mode
        subprocess.call(["chmod", "a+x", out])

        print("\nProcessed ecflow script %s" %out)



    def write_jjob2(self):
       
        lines="""#!/bin/sh 
 
date
export PS4=' $SECONDS + ' 
set -x 
 
export pgm="NWPS"
export pgmout=OUTPUT.$$
 
export KEEPDATA="YES"     # TODO - to see

PDY="$(date +'%Y%m%d')"

# temp location of the job working directory, typically $DATAROOT/$jobid 
export DATA=${{DATA:-${{DATAROOT:?}}/$jobid}}
mkdir -p $DATA   
cd $DATA

####################################
# Specify NET and RUN Name and model
####################################
export NET=${{model}}
#export RUN=$(echo ${{job}}|awk -F"_" '{{print $2}}')

####################################
# SENDECF  - Flag Events on ECFLOW
# SENDCOM  - Copy Files From TMPDIR to $COMOUT
# SENDDBN  - Issue DBNet Client Calls
####################################
export SENDCOM=${{SENDCOM:-YES}}
export SENDECF=${{SENDECF:-YES}}
export SENDDBN=${{SENDDBN:-NO}}

####################################
# Specify Execution Areas
####################################
export HOMEnsem=${{NWROOT}}
export FIXnsem=${{FIXnsem:-${{HOMEnsem}}/fix}}
export EXECnsem=${{EXECnsme:-${{HOMEnsem}}/exec}}
export SORCnsem=${{SORCnsem:-${{HOMEnsem}}/sorc}}
export PARMnsem=${{PARMnsem:-${{HOMEnsem}}/parm}}
export USHnsem=${{USHnsem:-${{HOMEnsem}}/ush}}

# Set processing DIRs here
export INPUTdir=${{INPUTdir:-${{DATA}}/input}}
export RUNdir=${{RUNdir:-${{DATA}}/run}}
export TMPdir=${{TMPdir:-${{DATA}}/tmp}}
export LOGdir=${{LOGdir:-${{DATA}}/logs}}

# Set NWPS run conditions
export DEBUGGING=${{DEBUGGING:-TRUE}}
export DEBUG_LEVEL=${{DEBUG_LEVEL:-1}}
export ISPRODUCTION=${{ISPRODUCTION:-TRUE}}
export SITETYPE=${{SITETYPE:-EMC}}

##############################################
# Define COM directory
##############################################
# com directory for current model's output data, typically $COMROOT/$NET/$envir/$RUN.$PDY
export COMOUT=${{COMROOT}}/${{envir}}/${{NET}}/{}.${{PDY}}
# nwges directory for output guess fields; typically $GESROOT/$envir
export GESOUT=${{GESROOT}}/${{envir}}/${{NET}}/{}.${{PDY}}
# nwges directory for input guess fields; typically $GESROOT/$envir
export GESIN=${{GESROOT}}/${{envir}}/${{NET}}/{}


# loop over nems.configure per model, also must match run_name
# COMIN com directory for current model's input data, typically $COMROOT/$NET/$envir/$RUN.$PDY 
# COMINmodel com directory for incoming data from model model 
export COMINatm=${{COMROOT}}/${{NET}}/${{envir}}/${{job}}/atm
export COMINwave=${{COMROOT}}/${{NET}}/${{envir}}/${{job}}/ww3
export COMINadc=${{COMROOT}}/${{NET}}/${{envir}}/${{job}}/adcirc
export COMINmeshdata=${{COMROOT}}/${{NET}}/${{envir}}/${{job}}/atmesh
export COMINnwm=${{COMROOT}}/${{NET}}/${{envir}}/${{job}}/nwm

mkdir -p $INPUTdir $RUNdir $TMPdir $LOGdir $COMOUT $GESOUT
##############################################
# Execute the script
${{HOMEnsem}}/scripts/ex{}
##############################################

#startmsg
msg="JOB $job HAS COMPLETED NORMALLY."
# postmsg $jlogfile "$msg"

if [ -e $pgmout ]; then
    cat $pgmout
fi

cd $DATAROOT

if [ "$KEEPDATA" != YES ]; then
    rm -rf $DATA
fi

date

""".format(self.RUN,self.RUN,self.RUN,self.RUN+".sh")
 
        outfile = os.path.join(self.jjob_dir(), "J"+self.RUN.upper())
        # running two storms at once, even for testing, overrides ecf files
        # p = self.storm_dir("job")
        # outfile = os.path.join(p, "J"+self.RUN.upper())
        with open(outfile, 'w') as fptr:
            fptr.write(lines)   

        # change mode
        subprocess.call(["chmod", "a+x", outfile])

        print("\nProcessed ecflow jjob script %s" %outfile)


        # create the script at the same time as jjob
        out = os.path.join(self.script_dir(),"ex"+self.RUN+".sh")

        # this script must exists that does the real work
        p = os.path.join(self.ush_dir(), self.RUN+".py")
        if not found(p):
            print("Warrning - make sure to prepare the script!")


        lines="""
echo "============================================================="
echo "=                                                            "
echo "=         RUNNING NSEM FOR STORM: {}                        
echo "=         RUN NAME: {}                              
echo "=                                                            "
echo "============================================================="
#
python ${{USHnsem}}/{}

echo "{} completed"
exit 0
""".format(self.NET, self.RUN, self.RUN+".py", self.RUN)

        with open(out, 'w') as fptr:
            fptr.write(lines)

        # change mode
        subprocess.call(["chmod", "a+x", out])

        print("\nProcessed ecflow script %s" %out)




class NEMSModel:

    def __init__(self, name, **kwargs):

        # holds kwargs i.e. attributes, petlist, ...
        self.__dict__.update({'Verbosity':'max'})  # default a must
        self.__name = name
        self.__dict__.update(**kwargs)


    @property
    def name(self):
        # i.e. ww3
        return self.__name


    @name.setter
    def name(self, name):
        self.__name = name


    def get_alias(self):
        name = self.name
        return self.__dict__[name.upper()+"_model"]


    def get_attributes(self):
        name = self.name
        return self.__dict__[name.upper()+"_attributes"]


    def get_petlist(self):
        """ gets pets lower and upper index """
        name = self.name
        return self.__dict__[name.upper()+"_petlist_bounds"]



class NEMSConfig(NCOSystem):

    """ processes nems.configure and model_configure file in PRJ_DIR """

    def __init__(self, node, user_module):

        super().__init__(model, event, envir, run_name, DATAROOT, GESROOT)

        self.node = node
        self.user_module = user_module

        self.read_nems_config()
        self.read_model_config()    


    def nems_config(self):
        return os.path.join(self.source_dir(), 'nems.configure')


    def model_config(self):
        return os.path.join(self.source_dir(), 'model_configure')


    def node(self):
        return self.node

    @property
    def user_module(self):
        return self.__user_module


    @user_module.setter
    def user_module(self, module):
        self.__user_module = os.path.join(self.source_dir(),'modulefiles', self.node, module)
        return(self.__user_module)


    def earth_model_names(self):
        return self.__dict__['EARTH_component_list']


    def nems_models(self):
        # holds a list of NEMSModel objects
        return self.__dict__['NEMS_component_list']


    def read_model_config(self):
      
        model_cf = self.model_config()
        print("\nReading NEMS config file %s" %model_cf)

        try:
          with open(model_cf,'r') as fptr:
            lines = fptr.readlines()
            for line in lines:
              if line.startswith("#") or len(line) < 2:
                continue
              key, value = line.split(":")
              if 'start_year' in key:
                self.start_year = value.strip()
              elif 'start_month' in key:
                self.start_month = value.strip()
              elif 'start_day' in key:
                self.start_day = value.strip()
              elif 'start_hour' in key:
                self.start_hour = value.strip()
              elif 'start_minute' in key:
                self.start_minute = value.strip()
              elif 'start_second' in key:
                self.start_second = value.strip()
              elif 'nhours_fcst' in key:
                self.nhours_fcst = value.strip()
        except Exception as e:
          print("\n%s" %str(e))
          sys.exit(-1)
      
        print("Finished reading NEMS config file %s" %model_cf)
        print("Runtime duration since: %s/%s/%s %s:%s:%s for %s hours" %(self.start_year,self.start_month,self.start_day,
               self.start_hour, self.start_minute, self.start_second, self.nhours_fcst))


    def get_duration(self):
        date_time_str = "%s/%s/%s %s:%s:%s" %(self.start_day, self.start_month, self.start_year, 
                                              self.start_hour, "00", "00")
        self.start_date = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S') 
        self.start_date_str = date_time_str
        return self.start_date, self.start_date_str


    def get_fcst_hours(self):
        return int(self.nhours_fcst)



    def read_nems_config(self):

        nems_cf = self.nems_config()
        print("\nReading NEMS config file %s" %nems_cf)
         
        try:
          with open(nems_cf,'r') as fptr:
            cnt = 0; sentinel = '::'
            # saves the line # of the "::" in file nems.configure
            indx = []
            lines = fptr.readlines()
            for line in lines:
              cnt += 1
              if line.startswith(sentinel):
                indx.append(cnt)

            # cut each section of the file based on indx  
            earth_list = []; model_list = []; seq_list = []

            earth_list = lines[:indx[0]]
            model_list = lines[indx[0]:indx[len(indx)-2]]
            seq_list = lines[indx[len(indx)-2]:]

            self.process_earth_section(earth_list)
            self.process_model_section(model_list)
            self.process_runseq_section(seq_list)

        except Exception as e:
            print("\n%s" %str(e))
            sys.exit(-1)

        print("Finished reading NEMS config file nems.configure")



    def get_num_tasks(self):
        """find the larget petlist number and save it as part of NEMSModel
           object for use in Slurm job """
        pl = []
        for model in self.nems_models():
            name = model.name
            petlist = model.get_petlist()
            pl.append(petlist[1])
        return max(pl)



    def print_model(self):
        for model in self.nems_models():
            name = model.name
            petlist = model.get_petlist()
            attrs = model.get_attributes()
            alias = model.get_alias()
            print("Model Name      : %s" %name)
            print("Model Alias     : %s" %alias)
            print("Model petlist   : %s" %petlist)
            print("Model attributes: %s" %attrs)
        print("\n")


    def process_earth_section(self, earth_lines):

        sentinel = '::'; i=0

        # lines are not cleaned yet
        lines = [line.strip() for line in earth_lines if len(line) > 1]
        line = lines[i]

        while line:
          #print("Line {}: {}".format(i, line.strip()))

          if re.search('EARTH_component_list', line, re.IGNORECASE) :
            k,v = line.split(":")
            models = list(v.split(" "))
            self.__dict__['EARTH_component_list'] = [model.strip() for model in models if len(model) > 1]
            i += 1
            line = lines[i]

          elif re.search('EARTH_attributes', line, re.IGNORECASE) :    # do not use :: becasue it might have space between!
            self.__dict__['EARTH_attributes'] = {}
            i += 1
            line = lines[i]

            while line.find(sentinel) == -1:
              dic = self.__dict__['EARTH_attributes']
              k,v = line.split("=")
              dic[k.strip()] = v.strip()
              self.__dict__['EARTH_attributes'] = dic
              i += 1
              line = lines[i]
            break

          else:      
            i += 1
            line = lines[i]     

        print("Pocessed EARTH_component_list")
        print(self.__dict__['EARTH_component_list'], "\n")



    def process_model_section(self, model_lines):

      sentinel = '::'; cnt = 0
      lines = [line.strip() for line in model_lines if len(line) > 2] 
      line = lines[cnt]


      self.__dict__['NEMS_component_list'] = []    
      tmp = []       # array for holding many NEMSModel objects
      i = 0          # counter of number of models in EARTH_component_list

      while( i < len(self.__dict__['EARTH_component_list']) ):
          model = self.__dict__['EARTH_component_list'][i]
          # print("Processing line %d, %s-%s, %d\n" %(cnt, line, model, i))

          if re.search(model+"_model", line, re.IGNORECASE) :   # do not use : becasue it might have space between!
              k,v = line.split(":")
              self.__dict__[model+"_model"] = v.strip()
              # print("1 - ", k, v.strip())
              cnt += 1
              line = lines[cnt]

          elif re.search(model+"_petlist_bounds", line, re.IGNORECASE) :
              k,v = line.split(":")
              v_int = [int(i) for i in list(v.strip().split(" "))]
              self.__dict__[model+"_petlist_bounds"] = v_int
              # print("2 - ", k, v_int)
              cnt += 1
              line = lines[cnt]

          elif re.search(model+"_attributes", line, re.IGNORECASE):
              self.__dict__[model+"_attributes"] = {}
              cnt += 1
              line = lines[cnt]
              while line.find(sentinel) == -1:
                  dic = self.__dict__[model+"_attributes"]
                  k,v = line.split("=")
                  dic[k.strip()] = v.strip()
                  self.__dict__[model+"_attributes"] = dic
                  cnt += 1
                  line = lines[cnt]
              # print("3 - ", k, dic)

              # update before breaking
              kwargs = { model+"_petlist_bounds":self.__dict__[model+"_petlist_bounds"],
                         model+"_attributes":self.__dict__[model+"_attributes"],
                         model+"_model":self.__dict__[model+"_model"]}
              tmp.append(NEMSModel(model,**kwargs))
              i += 1     # go to the next model in the list

          else:
              cnt += 1   # lines with comment or extera
              line = lines[cnt]
              
                

      # update before breaking
      self.__dict__['NEMS_component_list'] = tmp

      print("Processed models_component_list")
      self.print_model()
      



    def process_runseq_section(self, runseq_lines):

      sentinel = '::'; i = 0
      lines = [line.strip() for line in runseq_lines]
      line = lines[i]

      while True :
        # for now put this as common property -TODO
        if re.search('runSeq', line, re.IGNORECASE) :
          self.__dict__["runSeq"] = []
          vals = self.__dict__['runSeq']
          i += 1
          line = lines[i]
          
          while line.find(sentinel) == -1:
            vals.append(line.strip())
            i += 1
            line = lines[i]

          self.__dict__["runSeq"] = vals
          break
        else:
          i += 1
          line = lines[i]

      print("Processed runSeq")
      print(self.__dict__['runSeq'],"\n")


class NEMSBuild(NEMSConfig):

    """ This class creates a build script and copies the build file
        into PRJ_DIR, the same level as NEMS source location.
        Then runs the script to compile the system.

        It doesn't check for he correctness of the directory structure.
        It assumes all model's source are in same level of NEMS.

        # unique prj_dir sturcture is expected to be in this format per NCO standards:
        <PRJ_DIR>/     maps to NCO variable ==> ${NWROOT}
           |--- nsem??                      ==> HOMEmodel (i.e. $NWROOT/model.v X.Y.Z)  TODO - do we need this level??
           |--- sorc/                       ==> sorc
           |     |--- NEMS/   conf/   parm/   modulefiles/   model_configure  nems.configure  nems_env.sh  parm  
           |     |--- NWM/  WW3/  ADCIRC/  ATMESH/
           |     |--- esmf-impi-env.sh   build.sh   nems.job
           |     |--- 
           |     |---
           |--- ecf/   jobs/   scripts/   exec/*   fix/*   parm/*   /ush*

         All stared "*" directories have defined variables in NCO in the form of "VARmodel" (i.e. USHnsem, PARMnsem).
         See files in jobs/ directory where these variables are set. 
    """

   
    def __init__(self, node, user_module):

        super().__init__(node, user_module)   

        # we need the build.sh script to be available
        self.write_build()
           

    def write_build(self):

        source_dir = self.source_dir()
        user_module = self.user_module

        p = os.path.join(source_dir,'build.sh')
        print("\nProcessing build script %s" %p)
 
        junk, modulefile = user_module.split(source_dir)

        lines = """#!/bin/bash\n
# Description : Script to compile NSEModel NEMS application
# Date        : {}\n
# Developer   : beheen.m.trimble@noaa.gov
# Contributors: saeed.moghimi@noaa.gov
#               andre.vanderwesthuysen@noaa.gov
#               ali.abdolali@noaa.gov


# load modules
source {}   

cd NEMS\n""".format(now(2), modulefile[1:])    # remove the '/' from string

        lines += '\n#clean up\n'
     
        for model in self.nems_models():
            alias = model.get_alias().upper()
            if not exist(os.path.join(source_dir, alias)):
                print("\nDirectory %s not found!" %alias)
          
            lines += 'make -f GNUmakefile distclean_' + \
                      model.name + ' COMPONENTS=' + \
                      '"' + model.name + '"\n'
        
        lines += 'make -f GNUmakefile distclean_NEMS COMPONENTS="NEMS"\n'

        lines += '\n#make\n'
        lines += 'make -f GNUmakefile build COMPONENTS="'

        for model in self.nems_models():
            lines += model.name + ' '
        lines = lines[:-1] + '"\n'

        with open(p, 'w') as fptr:
            fptr.write(lines)

        # change mode
        subprocess.call(["chmod", "a+x", p])


        # save 
        self.build_script = p 

        print("Finished processing build script file %s" %p)



    def build_nems_app(self):

        try:
            print("\nStart compiling ............\n")

            subprocess.run(['./build.sh'], cwd=self.source_dir(), check=True)
        except subprocess.CalledProcessError as err:
            print('Error in executing build.sh: ', err)

        print("Finished compiling ............\n")




class SlurmJob():

    # this class requires information from nems.configure,
    def __init__(self, **kwargs):

        self.__dict__ = {'account':'coastal', 'queue':'test', 'error':'nems.error', 
                         'jobname':'nems.job', 'time':420, 'output':'nems.out',
                         'mailuser':'All', 'ntasks':780, 'nodes':34,'slurm_dir':'.' 
                        }
        self.__dict__.update(**kwargs)

        if 'error' in kwargs:
            self.error = "j" + kwargs['error'] + ".err.log"
        if 'output' in kwargs:
            self.output = "j" + kwargs['output'] + ".out.log"
        if 'jobname' in kwargs:
            self.jobname = "j" + kwargs['jobname'] + ".job"


    def get_sbatch(self):
        return self.sbatch_part


    def print_kw(self):
        print(self.__dict__)


    def write_sbatch(self):

        slurm_file = os.path.join(self.slurm_dir, self.jobname[1:])   # no j in this name, using this in standalone runs not in WCOSS

        sbatch_part = """#!/bin/sh -l\n
#SBATCH -A {}
#SBATCH -q {}
#SBATCH -e {}
#SBATCH --output={}
#SBATCH --ignore-pbs
#SBATCH -J {}
#SBATCH --mail-user={}
#SBATCH --ntasks-per-node={}
#SBATCH -N {}
#SBATCH --parsable
#SBATCH -t {}""".format(self.account,self.queue,self.error,self.output,self.jobname,
                        self.mailuser, self.ntasks, self.nodes, self.time)

        # for use by other classes
        self.sbatch_part = sbatch_part

        lines = """\n\n############################### main - to run: $sbatch {} ##########################
set -x
echo $SLURM_SUBMIT_DIR		# (in Slurm, jobs start in "current dir")   
echo $SLURM_JOBID                                                     
echo $SLURM_JOB_NAME
echo $SLURM_NNODES                                             
echo $SLURM_TASKS_PER_NODE\n
echo $SLURM_NODELIST		# give you the list of assigned nodes.\n
echo 'STARTING THE JOB AT'
date\n
# change to absolute path of where you pulled the 
# NEMS and NEMS Applications. use modules.nems becasue user's
# modulefiles are copied into this with constant name.
cp -fv {}/NEMS/exe/NEMS.x NEMS.x
source {}/NEMS/src/conf/modules.nems
srun ./NEMS.x
date
""".format(self.jobname, PRJ_DIR, PRJ_DIR )

        with open(slurm_file, 'w') as f:
            f.write(sbatch_part+lines)
        print("\nWrot slurm job file %s" %slurm_file)



class NEMSRun():

    # this class requires information from NCOSystem and SlurmJob
    def __init__(self, **kwargs):

        self.__dict__.update(**kwargs)  # TODO - add check that all args are in kwargs



class BlankLinesHelpFormatter (argparse.HelpFormatter):
    # add empty line if help lines ends with \n
    # default with=54
    def _split_lines(self, text, width):

        # default _split_lines removes final \n and reduces all interior whitespace to one blank
        lines = super()._split_lines(text, width)
        if text.endswith('\n'):
            lines += ['']
        return lines



if __name__ == '__main__':

    print("\n")  # this is to print nicer
    prog = sys.argv[0]
    usage = Color.F_Blue + "%s\n"  %prog
    usage += Color.F_Red
    usage += "       %s --help | -h \n"  %prog
    usage += "       %s --region <region> --node <node> --event <event> --module <user_module> --runname <run_name> --prjdir <prj_dir> --rundir <run_dir>\n" %(prog)
    usage += "       %s -R <region> -n <node> -e <event> -u <user_module> -s <run_name> -p <prj_dir> -r <run_dir>\n" %(prog)
    usage += "./start_workflow.py -n hera -e shinnecock -u ESMF_NUOPC -s tide_spinup -p /scratch2/COASTAL/coastal/save/NAMED_STORMS/COASTAL_ACT -r /scratch2/COASTAL/coastal/scrub/com/nsem"
    usage += Color.F_Default 

    desc = '''This script builds one or more coupled models with NEMS and/or installs the system into a pre-defined location, ready to run.\n'''
    parser = argparse.ArgumentParser(prog=prog, usage=usage, add_help=True,
                                     formatter_class=BlankLinesHelpFormatter,
                                     description=desc, epilog='\n')

    parser.add_argument('-p', '--prjdir', dest='prj_dir', type=str, default=PRJ_DIR,  
                        help='''Compiles, links, and creates libraries from the models source files using the NEMS coupler. Location of the coupled system could be provided by the user, as long as the specified location complies with the expected structure. The default project directory is {}\n'''.format(PRJ_DIR)) 
                                 
    parser.add_argument('-r', '--rundir', dest='run_dir', type=str, default=RUN_DIR, 
                        help='''Model inputfiles and model runtime directory. The default run directory is {}\n'''.format(RUN_DIR))

    parser.add_argument('-R', '--region', dest='region_name', type=str, default="CONUS", help='CONUS or Gulf or Atlantic - modeling region. The default region is CONUS\n')
    parser.add_argument('-n', '--node', dest='node_name', type=str, help='Name of the machine your are running this program from such as "hera". This name must be the same name as in conf/configure.nems.hera.<compiler>\n')
    parser.add_argument('-e', '--event', dest='event_name', type=str, help='A Named Storm Event Model such as "Sandy"\n')
    parser.add_argument('-u', '--module', dest='user_module', type=str, help='NEMS user module name, located in NEMS/modulefiles\n')
    parser.add_argument('-s', '--runname', dest='run_name', type=str, help='A unique name for this model run\n')

    parser.add_argument('-c', '--compile', type=int, choices=[0,1], default=0, help="Compile/build the source codes. Default is not to build\n")

    #parser.add_argument('-m', '--models', dest='model_list', type=str, help='Comma separated model directory names where the model source code resides at the same level of NEMS source codes. No space before and after commas. The model names are case sensative. Example: ADCIRC,WW3,NWM\n')

    args = parser.parse_args()
    print(len(sys.argv))

    """ Currently these cases have been identified
    'tide_baserun'        # Tide-only forecast run with ADCIRC
    'best_track2ocn'      # Best-track ATMdata used to force live ADCIRC  
    'wav&best_track2ocn'  # Best-track ATMdata and WAVdata used to force live ADCIRC  
    'atm2ocn'             # ATMdata used to force live ADCIRC  
    'wav2ocn'             # WAVdata used to force live ADCIRC  
    'atm&wav2ocn'         # ATMdata and WAVdata used to force live ADCIRC  
    'atm2wav2ocn'         # ATMdata used to force live ADCIRC and WW3 
    """

    # local variables from comman lines
    region = node = event = user_module_name = run_name = ""

    compile = args.compile
    region = args.region_name
    node = args.node_name
    event = args.event_name
    user_module_name = args.user_module
    run_name = args.run_name
    RUN_DIR = args.run_dir    # update - Note: add the nsem as part of rundir
    PRJ_DIR = args.prj_dir    # update
    DATAROOT = os.path.join("/tmp",event.lower())
    GESROOT = os.path.join(RUN_DIR,"nwgs")
    envir = "para"
    model = "nsem"

    if not exist(PRJ_DIR):
        print("Project directory %s doesn't exist, please check and rerun the program\n" %PRJ_DIR)
        sys.exit(-1)

    # construct model input/output paths, if none exists
    # or few it creates the none existing ones
    nco = NCOSystem(event, envir, run_name, DATAROOT, GESROOT, model=model)
    nco.setup_rundir()

    # update the prj_dir for new storm event - TOO
    # <prj_dir>/parm/<event> - to exists
    # <prj_dir>/fix/meshes/<event>   hsofs  hsofs_elevated20m ??
    # <prj_dir>/sorc/runupforecast.fd ??
    nco.setup_prjdir()
    source_dir = nco.source_dir()

    # populate NEMS model class and process nems configure files
    # needed for creation of build script
    nems_cfg = NEMSConfig(node, user_module_name)  # superclass to NEMSBuild 
    ntasks = nems_cfg.get_num_tasks()
    walltime = nems_cfg.get_fcst_hours()           # are they the same ??
    start_date, start_date_str = nems_cfg.get_duration()


    # compile the codes and submit the job to run
    nems_build = NEMSBuild(node, user_module_name)   # TODO pickle
    if compile:
        nems_build.build_nems_app()


    # SlurmJob needs update by reading nems.configure, 
    slurm_args = {'account':'coastal','ntasks':ntasks,'nnodes':'34','queue':'test',
                  'time':walltime,'jobname':run_name,'error':run_name,
                  'output':run_name,'mailuser':'??', 'slurm_dir': source_dir
                 }
    slurm = SlurmJob(**slurm_args)
    slurm.write_sbatch()

    # ecflow file constructions, requires info from both Slurm and NCO
    nco.write_ecf2(slurm)
    nco.write_jjob2()

    # create a importable file of all the environments needed
    nco.write_helper(nems_cfg)

    print("\n")

    # nems_run = NEMSRun(**run_args)

    # environment variable `$NSEMdir` that points to the location of the cloned code
    # The scratch directory with the model runs is:
    # /scratch2/NCEPDEV/stmp1/Andre.VanderWesthuysen/data
    # /scratch2/NCEPDEV/stmp1/Andre.VanderWesthuysen/data/shinnecock.atm2wav2ocn.20200528
    # Root directory for application, typically /nw$envir 
    # After the jnsem_post.ecf job is complete, the *.nc output is put in the following directory:
    # /scratch2/NCEPDEV/stmp1/Andre.VanderWesthuysen/data/com/nsem/para/shinnecock.atm2wav2ocn.20200528

    """
6) From the test run example you provided, I understood the location of each model's input files is in data/com per combination of event and run_type. Is this correct?
Not quite. The RUN_TYPE (Saeed's original "run_option") is associated with the different types of NSEM runs, and thus their *output*. So the *output* of the NSEM in COM is stored under $STORM.$RUN_TYPE. However, the inputs to NSEM are not stored like that in COM, because there is no RUN_TYPE associated with, for example, the HWRF wind fields, or the WW3 boundary conditions. So they are just stored as COM/hwrf and COM/ww3. Does that make sense?

7) How do we plan to put the model's data in its location with correct naming?
We would all need to agree that COM is the standard location for all inputs/outputs, as required by NCO. Then the HWRF runs will write their output to COM/hwrf. This in turn will become the (partial) input to NSEM. Then, when NSEM runs, its output will be written to COM/nsem/$STORM.$RUN_TYPE. From there it will go to AWS/CWWED. So if we all write to, or read from COM in our scripting, the system will work. For NSEM, the paths of these input streams are set with the env variables COMIN by storm in the jobs/ scripts.

8) Is the model compilation part of this process?
We discussed this one on our previous call. We don't strictly need to do this in our operational workflow, since we can run subsets of the NEMS app without changing the NEMS.x, as Saeed pointed out. This is also not typically done in NCO operations, since it takes a bit of time. This is of course different from our regression testing, where the code needs to be compiled each time we go through the CI workflow. This is part of the compsets we have in our old VLab version of our app, and it still needs to be brought over to our Git version.

9) How did you produce the jjob file? It seems that there are many variables that need to be updated per unique run?
The jjob file is a standard template constructed manually. The runtime variables that need to be updated come from the env variables such as $STORM and $RUN_TYPE. Are there others you can think of that we need to incorporate? 

I didn't use ww3data to test the coupled app/workflow. However, I did maintain the functionality in the workflow for the cases where we want to use it (e.g. get stand-alone ADCIRC results). For this, you need to set COMINwavdata to the ww3data/ folder in COM, and use the RUN_TYPE = atm&wav2ocn. But this won't be our main "happy path" user story.
"""
