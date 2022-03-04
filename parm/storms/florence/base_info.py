"""
Config file for NSEModel run generator
All filenames relative to main directories
FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE  Config file
FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE  Config file
FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE FLORENCE  Config file
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
    'atm2wav2ocn',
    'atm2wav-ocn'  
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
tide_spin_start_date   = datetime.datetime(2018,8,27,18,0,0) # this is also tde_ref_date (tide_fact calc)
#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=34.0)
#final_end_date        = tide_spin_start_date + datetime.timedelta(days=23.5)

tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=20.5)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=16.5)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=16.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=20.5)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=12.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=15.0)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=15.0)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=17.5)

#tide_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=17.5)
#wave_spin_end_date     = tide_spin_start_date + datetime.timedelta(days=20.0)

# Folders
#main_run_dir    = '/scratch4/COASTAL/coastal/noscrub/Saeed.Moghimi/stmp5/'   # IKE test cases
#application_dir = '/scratch4/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/tests/NSEModel_try_err_branches/HWRF2ADC_test02/'
#app_inp_dir     = '/scratch4/COASTAL/coastal/save/Saeed.Moghimi/models/NEMS/NEMS_inps/nsemodel_inps/'

# modules inp dirs
#grd_inp_dir     = 'hsofs_grid_v1/'                                #relative to  $app_inp_dir/
#ocn_inp_dir     = 'hsofs_forcings/ike_v1/inp_adcirc/'          #relative to  $app_inp_dir/

mesh = 'hsofs'

# Plotting domains
lonmin_plot_full=-100.00
lonmax_plot_full=-50.00
latmin_plot_full=5.00
latmax_plot_full=50.00
lonmin_plot_regional=-84.00
lonmax_plot_regional=-64.00
latmin_plot_regional=24.00
latmax_plot_regional=42.00
lonmin_plot_landfall=-80.40
lonmax_plot_landfall=-74.75
latmin_plot_landfall=32.50
latmax_plot_landfall=36.60
#lonmin_plot_landfall=-77.20
#lonmax_plot_landfall=-77.05
#latmin_plot_landfall=34.55
#latmax_plot_landfall=34.70

# Interval for 90% accuracy analysis
#analysis_start_date   = datetime.datetime(2018,9,9,6,0,0)
analysis_start_date   = datetime.datetime(2018,9,12,0,0,0)
#analysis_end_date   = datetime.datetime(2018,9,17,0,0,0)
#analysis_end_date   = datetime.datetime(2018,9,15,0,0,0)
analysis_end_date   = datetime.datetime(2018,9,16,5,0,0)

   #reflon=np.linspace(-75.70, -71.05, 1000)
   #reflat=np.linspace(38.50, 41.40, 1000)

#atm_inp_dir     = 'hsofs_forcings/ike_v2_7settings/inp_atmesh'     
#wav_inp_dir     = 'hsofs_forcings/ike_v2_7settings/inp_wavdata' 
   
#wave and atm files are 
atm_netcdf_file_names = np.array([
#    'Florence_HWRF_HRRR_HSOFS.wrfles.nc',
    'Florence_HWRF_HRRR_HSOFS.nc',
#    'windOut-Florence.nc4',
    ])
    
wav_netcdf_file_names = np.array([
    '07_ww3.test7.2008_sxy_OC_DA_WRF_SM.nc',
    ])

if run_option == 'tide_spinup':    
    # To prepare a clod start ADCIRC-Only run for spining-up the tide 
    Ver             = 'v2.0'
    RunName         = 'a21_IKE_OCN_SPINUP'         # Goes to qsub job name
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
    RunName         = 'a21_IKE_TIDE'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
    ihot            = 67
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'best_track2ocn':    
    Ver             = 'v2.0' 
    RunName         = 'a22_IKE_BEST'           # Goes to qsub job name
    #inp files
    fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
    RunName         = 'a23_IKE_WAV2BEST'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
    RunName         = 'a37_IKE_ATM2OCN'           # Goes to qsub job name
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
    #AW ndays_ramp      = 5.0
    ndays_ramp      = '7.000 0.000 0.000 0.000 7.000 7.000 1.000 0.000 7.000'
    nws             = 17       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt    
elif run_option == 'wav2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a47_IKE_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
elif run_option == 'atm2wav':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a57_IKE_ATM2WAV'            # Goes to qsub job name
    #inp files
    fort15_temp     = ''           
    ww3_multi_tmpl  = 'ww3_multi.inp.sbs.tmpl'
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
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt
    hot_wave_out    = (wave_spin_end_date - tide_spin_end_date).total_seconds()   
elif run_option == 'atm&wav2ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a57_IKE_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
    RunName         = 'a57_IKE_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
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
    #AW ndays_ramp      = 5.0
    ndays_ramp      = '7.000 0.000 0.000 0.000 7.000 7.000 1.000 0.000 7.000'
    nws             = 517       # atm  Deprecated
    ihot            = 567
    hot_ndt_out     = ndays * 86400 / dt
    hot_wave_out    = (wave_spin_end_date - tide_spin_end_date).total_seconds()
elif run_option == 'atm2wav-ocn':    
    Ver             = 'v1.0_7t' 
    RunName         = 'a57_IKE_ATM_WAV2OCN'            # Goes to qsub job name
    #inp files
    fort15_temp     = 'fort.15.template.atm2ocn'           
    #fetch_hot_from  = main_run_dir + '/a21_IKE_OCN_SPINUP_v1.0/rt_20170712_h16_m12_s57r072/'
    ww3_multi_tmpl  = 'ww3_multi.inp.sbs.tmpl'
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
    nws             = 17       # atm  Deprecated
    ihot            = 567
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
elif run_option == 'atm2wav':    
    #NEMS settings
    nems_configure  = 'nems.configure.atm_wav.IN' 
    #
    atm_name     = 'atmesh' 
    atm_petlist  = '0 0'
    #
    ocn_name     = None
    # 
    wav_name     = 'ww3'
    wav_petlist  = '1 719' 
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
    #wav_petlist  = '721 2159'
    #  
    coupling_interval_sec      = 900 
    #
elif run_option == 'atm2wav-ocn':    
    #NEMS settings
    nems_configure  = 'nems.configure.atm_ocn_wav_sbs.IN' 
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

