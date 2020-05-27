"""
Config file for NSEModel run generator
All filenames relative to main directories
CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK  Config file
CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK  Config file
CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK CHINNECOCK  Config file
"""

__author__ = 'Saeed Moghimi'
__copyright__ = 'Copyright 2017, NOAA'
__license__ = 'GPL'
__version__ = '1.1'
__email__ = 'moghimis@gmail.com'


import numpy as np
import os,sys
import datetime

#######################
### Input data here ###
#qsub information
WallTime   = '00:30:00'                  # Maximize scheduling through HH:MM:SS
Queue      = 'batch'                     # 'batch' 'debug'
#-----------------------------------
# Choose options by commenting out

avail_options = [
    'tide_spinup',
    'tide_baserun',
    'best_track2ocn',
    'wav&best_track2ocn',
    'atm2ocn',
    'wav2ocn',
    'atm&wav2ocn', 
    'atm2wav2ocn'   
    ]

#Choose one option based on avail_options
run_option = os.getenv('RUN_TYPE')
#run_option = 'tide_spinup'
#run_option = 'tide_baserun'
#run_option = 'best_track2ocn'
#run_option = 'wav&best_track2ocn'
#run_option  = 'atm2ocn'
#run_option = 'wav2ocn'    ####>>>> Not supported. Best is to get diff of atm&wav2ocn and atm2ocn to see the wave effects
#run_option = 'atm&wav2ocn'   # ATMdata and WAVdata used to force live ADCIRC
#run_option = 'atm2wav2ocn'   # ATMdata used to force live ADCIRC and WW3
#----------------------------------
#Date settings
tide_spin_start_date = datetime.datetime(2008,8,23,0,0,0) # this is also tde_ref_date (tide_fact calc)
tide_spin_end_date   = tide_spin_start_date + datetime.timedelta(days=12.5)
wave_spin_end_date   = tide_spin_start_date + datetime.timedelta(days=27)
#final_end_date      = tide_spin_start_date + datetime.timedelta(days=23.5)

# Folders
#main_run_dir    = '/scratch2/COASTAL/coastal/noscrub/Saeed.Moghimi/01_stmp_ca/stmp1-chi_nems_v2/'   # florence test cases
#application_dir = '/scratch2/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/tests/new_nems_app/ADC-NEMS-APP-V2/'
#app_inp_dir     = '/scratch2/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/NEMS_inps/nsemodel_inps/'

# modules inp dirs
#grd_inp_dir = 'chinnecock_grid_v2/'                         #relative to  $app_inp_dir/
#ocn_inp_dir = 'chinnecock_forcing_v2/inp_adcirc/'           #relative to  $app_inp_dir/

mesh = 'shinnecock'

#atm_inp_dir = 'chinnecock_forcing_v2/inp_atmesh/'           #relative to  $app_inp_dir/
#wav_inp_dir = 'chinnecock_forcing_v2/inp_wavdata/'          #relative to  $app_inp_dir/

#wave and atm files are 
atm_netcdf_file_names = np.array([
    'wind_atm_fin_ch_time_vec.nc',
    ])

wav_netcdf_file_names = np.array([
    'ww3.Constant.20151214_sxy_ike_date.nc',
    ])

if run_option == 'tide_spinup':    
    # To prepare a clod start ADCIRC-Only run for spining-up the tide 
    Ver             = 'v10.0'
    RunName         = 'a10_CHI_OCN_SPINUP'         # Goes to qsub job name
    #inp files
    fetch_hot_from  = None
    fort15_temp     = 'fort.15.template.tide_spinup'           
    # Time
    start_date      = tide_spin_start_date
    start_date_nems = tide_spin_start_date
    end_date        = tide_spin_end_date
    dt              = 2.0     
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7
    nws             = 0        #no wave no atm    Deprecated
    ihot            = 0        #no hot start
    hot_ndt_out     = ndays * 86400 / dt
elif run_option == 'tide_baserun':    
    Ver             = 'v2.0-test' 
    RunName         = 'a20_CHI_TIDE'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    fort15_temp     = 'fort.15.template.tide_spinup'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 0        # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'best_track2ocn':    
    Ver             = 'v1.1' 
    RunName         = 'a30_CHI_BEST'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    fort15_temp     = 'fort.15.template.atm2ocn'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    # 
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 20        # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'wav&best_track2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a40_CHI_WAV2BEST'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 520    
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a50_CHI_ATM2OCN'           # Goes to qsub job name
    #inp files
    #fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    fort15_temp     = 'fort.15.template.atm2ocn'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 17       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'wav2ocn':    
    Ver             = 'v10.0'
    RunName         = 'a60_CHI_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 500       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm&wav2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a70_CHI_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    #Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 517       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm2wav2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a70_CHI_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a10_CHI_OCN_SPINUP_v10.0/rt_20180531_h13_m01_s30r830'
    ww3_multi_tmpl  = 'ww3_multi.inp.tmpl'
    ww3_ounf_tmpl   = 'ww3_ounf.inp.tmpl'
    wbound_flg      = True
    #Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 7.0
    nws             = 517       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt  
else:
    print('">',run_option, '< " is not a valid option !')
    print('Here is the list of the valid options: ', avail_options)
    sys.exit('STOP !')


#Nems settings
if run_option in ['tide_spinup','tide_baserun','best_track2ocn']:    
    #NEMS settings
    nems_configure  = 'nems.configure.ocn.IN' 
    ocn_name     = 'adcirc'
    ocn_petlist  = '0 10'
    #
    atm_name     = None
    wav_name     = None  
    #
    coupling_interval_sec      = 3600  
    #
elif run_option == 'atm2ocn':    
    #NEMS settings
    nems_configure   = 'nems.configure.atm_ocn.IN' 
    # model components
    ocn_name     = 'adcirc'
    ocn_petlist  = '0 10'
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '11 11'
    #
    wav_name     = None
    #
    coupling_interval_sec      = 3600
    #
elif run_option in ['wav2ocn','wav&best_track2ocn']:    
    #NEMS settings
    nems_configure   = 'nems.configure.wav_ocn.IN' 
    # model components
    ocn_name     = 'adcirc'
    ocn_petlist  = '0 10'
    #
    wav_name     = 'ww3data'
    wav_petlist  = '11 11'  
    #
    atm_name     = None
    #
    coupling_interval_sec      = 3600
    #
elif run_option == 'atm&wav2ocn':    
    #NEMS settings
    nems_configure  = 'nems.configure.atm_ocn_wavdata_1loop.IN' 
    #
    ocn_name     = 'adcirc'
    ocn_petlist  = '0 10'
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '11 11'
    # 
    wav_name     = 'ww3data'
    wav_petlist  = '12 12'  
    #
    coupling_interval_sec      = 3600  
    #
elif run_option == 'atm2wav2ocn':    
    #NEMS settings
    nems_configure  = 'nems.configure.atm_ocn_wav_1loop.IN' 
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '0 0'
    #
    ocn_name     = 'adcirc'
    ocn_petlist  = '1 11'
    # 
    wav_name     = 'ww3'
    wav_petlist  = '12 22' 
    #  
    coupling_interval_sec      = 900 
    #

# may be better to move it to main code
if nws > 0 :
    # ADCIRC wave forcing time interval
    RSTIMINC = str (coupling_interval_sec)  + ' '
    if nws in[20,520]:
        #best track value setting
        StormNumber = 1
        BLAdj = 0.9
        Geofactor = 1
        WTIMINC = tide_spin_start_date.strftime('%Y %m %d %H') + ' ' + str(StormNumber) + ' ' + str(BLAdj) + ' ' + str (Geofactor) + ' '
    else:
        WTIMINC = str (coupling_interval_sec)  + ' ' # ADCIRC atm forcing time interval

# relative to $application_dir/
module_file     = 'modulefiles/hera/ESMF_NUOPC'
qsub_tempelate  = 'slurm.hera.template'
# Templates
qsub            = 'qsub.template' 
model_configure = 'atm_namelist.rc.template'

