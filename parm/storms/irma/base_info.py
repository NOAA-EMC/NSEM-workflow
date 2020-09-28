"""
Config file for NSEModel run generator
All filenames relative to main directories
IRMA IRMA IRMA IRMA IRMA IRMA IRMA IRMA  Config file
IRMA IRMA IRMA IRMA IRMA IRMA IRMA IRMA  Config file
IRMA IRMA IRMA IRMA IRMA IRMA IRMA IRMA  Config file
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
WallTime   = '06:30:00'                  # Maximize scheduling through HH:MM:SS max long spin up
Queue      = 'batch'
#WallTime   = '00:30:00'                   # Maximize scheduling through HH:MM:SS  for normal runs
#Queue      = 'debug'                      # 'batch' 'debug'
#-----------------------------------
# Choose options by commenting out

avail_options = [
    'tide_spinup',
    'atm2ocn',
    'wav2ocn',
    'atm&wav2ocn', 
    'atm2wav2ocn'   
    ]

#Choose one option based on avail_options 
run_option = os.getenv('RUN_TYPE')
#run_option = 'tide_spinup'
#run_option  = 'atm2ocn'
#run_option = 'wav2ocn'    ####>>>> Not supported. Best is to get diff of atm&wav2ocn and atm2ocn to see the wave effects
#run_option = 'atm&wav2ocn'   # ATMdata and WAVdata used to force live ADCIRC
#run_option = 'atm2wav2ocn'   # ATMdata used to force live ADCIRC and WW3
#----------------------------------
#Date settings
tide_spin_start_date   = datetime.datetime(2017,8,23,12,0,0) # this is also tde_ref_date (tide_fact calc)
#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=19.5)
#final_end_date        = tide_spin_start_date + datetime.timedelta(days=23.5)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=16.5)

tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=16.5)
wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=19.5)

# Folders
#main_run_dir    = '/scratch4/COASTAL/coastal/noscrub/Saeed.Moghimi/stmp5/'   # IKE test cases
#application_dir = '/scratch4/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/tests/NSEModel_try_err_branches/HWRF2ADC_test02/'
#app_inp_dir     = '/scratch4/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/NEMS_inps/nsemodel_inps/'

# modules inp dirs
#grd_inp_dir     = 'hsofs_grid_v1/'                                #relative to  $app_inp_dir/
#ocn_inp_dir     = 'hsofs_forcings/ike_v1/inp_adcirc/'          #relative to  $app_inp_dir/

mesh = 'hsofs'

#atm_inp_dir     = 'hsofs_forcings/ike_v2_7settings/inp_atmesh'     
#wav_inp_dir     = 'hsofs_forcings/ike_v2_7settings/inp_wavdata' 
   
#wave and atm files are 
atm_netcdf_file_names = np.array([
    'IRMA_HWRF_HSOFS_Nov2018.nc',
    ])
    
wav_netcdf_file_names = np.array([
    '',
    ])

if run_option == 'tide_spinup':    
    # To prepare a clod start ADCIRC-Only run for spining-up the tide 
    Ver             = 'v2.0'
    RunName         = 'a21_IRMA_OCN_SPINUP'         # Goes to qsub job name
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
    ndays_ramp      = 5
    nws             = 0        #no wave no atm    Deprecated
    ihot            = 0        #no hot start
    hot_ndt_out     = ndays * 86400 / dt
elif run_option == 'tide_baserun':    
    Ver             = 'v2.0' 
    RunName         = 'a21_IRMA_TIDE'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    fort15_temp     = 'fort.15.template.tide_spinup'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 0        # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'best_track2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a22_IRMA_BEST'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    fort15_temp     = 'fort.15.template.atm2ocn'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    # 
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 20        # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'wav&best_track2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a23_IRMA_WAV2BEST'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 520    
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a37_IRMA_ATM2OCN'           # Goes to qsub job name
    #inp files
    #fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    fort15_temp     = 'fort.15.template.atm2ocn'           
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 17       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'wav2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a47_IRMA_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    # Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    #
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 500       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm&wav2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a57_IRMA_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    #Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 517       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'atm2wav2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a57_IRMA_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IRMA_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    ww3_multi_tmpl  = 'ww3_multi.inp.tmpl'
    ww3_ounf_tmpl   = 'ww3_ounf.inp.tmpl'
    wbound_flg      = True
    wbound_type     = 'nc'
    #Time
    start_date      = tide_spin_start_date  #current time is set by hotfile therefore we should use the same start time as 1st spinup
    start_date_nems = tide_spin_end_date
    end_date        = wave_spin_end_date
    dt              = 2.0   #######2.0    
    ndays           = (end_date - start_date).total_seconds() / 86400.  #duration in days
    #fort15 options
    ndays_ramp      = 5.0
    nws             = 517       # atm  Deprecated
    ihot            = 568
    hot_ndt_out     = ndays * 86400 / dt
    hot_wave_out    = (wave_spin_end_date - tide_spin_end_date).total_seconds()
else:
    print('">',run_option, '< " is not a valid option !')
    print('Here is the list of the valid options: ', avail_options)
    sys.exit('STOP !')


#Nems settings
if run_option in ['tide_spinup','tide_baserun','best_track2ocn']:    
    #NEMS settings
    nems_configure  = 'nems.configure.ocn.IN' 
    ocn_name     = 'adcirc'
    ocn_petlist  = '0 719'
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
    ocn_petlist  = '0 383'
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '384 384'
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
    ocn_petlist  = '0 382'
    #
    wav_name     = 'ww3data'
    wav_petlist  = '383 383'  
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
    ocn_petlist  = '0 381'
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '382 382'
    # 
    wav_name     = 'ww3data'
    wav_petlist  = '383 383'    
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
    ocn_petlist  = '1 720'
    # 
    wav_name     = 'ww3'
    wav_petlist  = '721 1439' 
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

