#!/usr/bin/env python

# stdandard libs
import os, sys, time, subprocess, logging, shutil
import json
from datetime import datetime, timedelta
from dateutil.parser import parser
from string import Template

# third party libs
import numpy as np

# user defined libs
import nsem_env as env
import nsem_utils as util

##########################################

"""
prepares model configurations, model input files, nems configuration per
storm and per run_name ready to be submitted to run.


questions:
what is the major work of nsem_prep? just input? input and spinup runs?
what is nws ??   dep. run_type
what are the PE runs used for and their relation to CA forecast run?
does tide and wave spin up always run before adc run?
tide_spinup','tide_baserun','best_track2ocn - not run_type??
How to calculate the spinup times? how to deal with < day remainder, set the 12.5, 27??
how get the wave and atm files during forecast time?
avail_options = [
    'tide_spinup',
    'atm2ocn',
     'wav2ocn',
    'atm&wav2ocn',
    ]
are these runs produces output that should be used in forcast run?
which option is required to be run back to back with forecast
how to calculate the spinup timing if the forcast hours is only few hours?
when False in base info runs?
how to read the nems.configure.xxx.IN files?
is storms directory ??
"""

logger = logging.getLogger(env.jlogfile)


def read_ini():
    """ reading user defined variables from initialization file, nsem_ini """
    ini_dict = {}
    try:
      with open('nsem_ini.py') as fptr:
        data = json.load(fptr)
    except Exception as err: 
        print("%s\n" %(str(err)))
        sys.exit(-1)

    
def get_tidal_fact():
    """
    based on spin-up start time prepare tide fac to be used in fort.15.tempelate
    In:
    Out: tidal fact dictionary
    
    """

    # copy tidal input file - TODO why in two places?? get example
    tide_spin_sdate, tide_spin_edate, wave_spin_sdate, wave_spin_edate, start_date, end_date = spinup_time()
    duration = str ((wave_spin_edate - tide_spin_sdate).total_seconds() /86400.)
    msg = """{} {} {} {} {}""".format(duration, tide_spin_sdate.hour, tide_spin_sdate.day, 
                                      tide_spin_sdate.month, tide_spin_sdate.year)
    tidefac_inp_file = os.path.join(env.COMINadc, 'tide_inp.txt')
    with open (tidefac_inp_file, 'w') as fpt:
        fpt.write(msg)

    
    tidefac_dic = {}
    tidefac_out_file = os.path.join(env.COMOUT, 'tide_fac.out')
    tidefac_out      = open(tidefac_out_file,'r')
    
    for line in tidefac_out.readlines():
        params = line.split()
        print(line)
        if 'K1'  in  params:    fft1,facet1   = params[1],params[2]
        if 'O1'  in  params:    fft2,facet2   = params[1],params[2]
        if 'P1'  in  params:    fft3,facet3   = params[1],params[2]
        if 'Q1'  in  params:    fft4,facet4   = params[1],params[2]
        if 'N2'  in  params:    fft5,facet5   = params[1],params[2]
        if 'M2'  in  params:    fft6,facet6   = params[1],params[2]
        if 'S2'  in  params:    fft7,facet7   = params[1],params[2]
        if 'K2'  in  params:    fft8,facet8   = params[1],params[2]
        if 'MF'  in  params:    fft9,facet9   = params[1],params[2]
        if 'MM'  in  params:    fft10,facet10 = params[1],params[2]
        if 'M4'  in  params:    fft11,facet11 = params[1],params[2]
        if 'MS4' in  params:    fft12,facet12 = params[1],params[2]
        if 'MN4' in  params:    fft13,facet13 = params[1],params[2]
    tidefac_out.close()
   
    return dict ( fft1=fft1,facet1=facet1,   
                  fft2=fft2,facet2=facet2,   
                  fft3=fft3,facet3=facet3,   
                  fft4=fft4,facet4=facet4,   
                  fft5=fft5,facet5=facet5,   
                  fft6=fft6,facet6=facet6,   
                  fft7=fft7,facet7=facet7,   
                  fft8=fft8,facet8=facet8,   
                  fft9=fft9,facet9=facet9,   
                  fft10=fft10,facet10=facet10, 
                  fft11=fft11,facet11=facet11, 
                  fft12=fft12,facet12=facet12, 
                  fft13=fft13,facet13=facet13
               ) 




""" to check the caclulation wit engineers """
def spinup_time(ts=12.5,ws=27):

    """calculates spinup timing for both tide and wave 
       relative to forecast start time and end time """

    duration = env.frcst_hrs
    start_date_str = env.start_date_str

    # string date to date object
    start_date = datetime.strptime(start_date_str, '%m/%d/%Y %H:%M:%S')
    hours_added = timedelta(hours=duration)
    end_date = start_date + hours_added
    delta = end_date - start_date
    num_days = delta.days
    # print(start_date, end_date, num_days)

    # tide spinup start time must be 12 days prior to forecast start date
    tide_spin_start_date = start_date - timedelta(days=ts)
    # wave spinup star time must be 27 prior to start date
    wave_spin_start_date = start_date - timedelta(days=ws)

    tide_spin_end_date = tide_spin_start_date + timedelta(days=ts)
    wave_spin_end_date = wave_spin_start_date + timedelta(days=ws)
    # 2008-08-23 00:00:00
    # 2008-09-04 12:00:00
    # 2008-09-19 00:00:00
    # print("Start wave: %s\nStart tide: %s\nEnd tide  : %s\nEnd wave  : %s\nStart date: %s\nEnd date  : %s\n"                                          
    #        %(wave_spin_start_date, tide_spin_start_date, tide_spin_end_date,           
    #         wave_spin_end_date, start_date, end_date))

    msg = tide_spin_start_date, tide_spin_end_date, wave_spin_start_date, wave_spin_end_date, start_date, end_date
    logger.info(msg)
    return msg


""" must be adjusted based on HWRF+ADC data file name standards """
def adc_atm_data():
    # Is this the atmesh or atm app_inp_dir = /scratch2/COASTAL/coastal/save/NAMED_STORMS/NSEM_app_run_workflow/nsemodel_inps
    # copping atm data from COMINatm
    # (i.e. /scratch2/COASTAL/coastal/scrub/com/nsem/para/shinnecock/atm)

    atm_inp_dir     = env.COMINatm           # 'hsofs_forcings/ike_v2_7settings/inp_atmesh'
    wav_inp_dir     = env.COMINwav           # 'hsofs_forcings/ike_v2_7settings/inp_wavdata'

    # atm files are 
    # what was in wind_atm_fin.nc  wind_atm_fin_ch_time_vec.nc
    atm_netcdf_file_names = [
        '01_IKE_HWRF_OC.nc',
        '02_IKE_HWRF_OC_SM.nc',
        '03_IKE_WRF.nc',
        '04_IKE_HWRF_OC_WRF.nc',
        '05_IKE_HWRF_OC_DA_HSOFS_orig.nc',
        '06_IKE_HWRF_OC_DA_HSOFS_Smoothing.nc',
        '07_IKE_HWRF_OC_DA_WRF_SM.nc',
        ]



""" must be adjusted based on some standard naming or copied manually """
def adc_wave_data():

    wav_netcdf_file_names = [
        '01_ww3.test1.2008_sxy_OC.nc',
        '02_ww3.test2.2008_sxy_OC_SM.nc',
        '03_ww3.test3.2008_sxy_WRF.nc',
        '04_ww3.test4.2008_sxy_OC_WRF.nc',
        '05_ww3.test5.2008_sxy_OC_DA_HSOFS_orig.nc',
        '06_ww3.test6.2008_sxy_OC_DA_HSOFS_Smoothing.nc',
        '07_ww3.test7.2008_sxy_OC_DA_WRF_SM.nc',
        ]
    return (file for file in wav_netcdf_file_names)


""" is this needed ??? """
def change_nws():
    """ 
    Go through all fort.15 files and change nws. I need
    this routine because adcprep still not addapted to handl nws=17.
    """
    import glob

    sys.exit( 'Fixed internally. Go ahead and chenge your main fort.15 if needed!')

    pattern = 'NWS'
    nws     = str (base_info.nws)
    line2replace  = ' ' +nws+ \
        '                                       ! NWS - WIND STRESS AND BAROMETRIC PRESSURE \n'
    #replace main fort.15
    filename = os.path.join(run_dir,'fort.15')
    replace_pattern_line( filename = filename , pattern = pattern, line2replace = line2replace )

    #replace fort.15 in PE directories

    dirs = glob.glob(run_dir + '/PE0*')

    for dir1 in dirs:
         filename = os.path.join(dir1,'fort.15')
         replace_pattern_line( filename = filename , pattern = pattern, line2replace = line2replace )

    print(' > Finished updating  fort.15s')
   #####
    pattern = 'NWS'
    nws     = str (base_info.nws)
    line2replace  = '       ' + nws + \
        '                        ! NWS, wind data type \n'
    filename = os.path.join(run_dir,'fort.80')
    replace_pattern_line( filename = filename , pattern = pattern, line2replace = line2replace )
    print(' > Finished updating  fort.80')




def update_fort15(dic):
    """update adcirc model parameter and periodic boundary condition 
       file (fort.15). fort.15 is a template file and it is updated
       once per storm and under certain condition per run-type"""

    # get information needed from nems_env.py file
    start_date_str = env.start_date_str
    duration = env.frcst_hrs

    # change the date format to what adcirc expects
    start_date = datetime.strptime(start_date_str, '%m/%d/%Y %H:%M:%S')
    adcirc_start_date = start_date.isoformat().replace('T',' ')+ ' UTC'
    
    # saves the updateable parameters
    d15 = {}
    d15.update({'start_date'    :adcirc_start_date })
    d15.update({'run_time_days' :str(dic['ndays'])})

    d15.update({'dramp'         :str(dic['ndays_ramp'])})
    d15.update({'nws'           :str(dic['nws'])})
    d15.update({'ihot'          :str(dic['ihot'])})
    d15.update({'dt'            :str(dic['dt'])})
    d15.update({'hot_ndt_out'   :str(dic['hot_ndt_out'])})

    if dic['nws'] > 0:
        d15.update({'WTIMINC'       :str(base_info.WTIMINC)  })
        d15.update({'RSTIMINC'      :str(base_info.RSTIMINC)  })
        #os.system('cp -f ' + adc_inp + '/fort* ' + run_dir)
        #os.system('cp -f ' + adc_inp + '/*.sh  ' + run_dir)
        #os.system('cp -f ' + adc_inp + '/*.py  ' + run_dir)
        os.system ('cp -f ' + adc_inp + '/*.*   ' + run_dir)

    # get tide facts - TODO needs a condition
    
    """ TODO Condition ?? """
    #d15_tide = get_tidal_fact(run_dir)
    #d15.update(d15_tide)

    # get updated fort.15
    fort15tmp = os.path.join(env.FIXnsem,'meshes',env.storm,'ocn', dic['fort15_temp'])
    dest  = os.path.join(env.COMINadc,'fort.15')
    util.tmp2scr(filename=dest, tmpname=fort15tmp, d=d15)



""" must be communicated on how to automate the build and the jobfile """
def prep_nems(dic):
  
    """Prepare nems run files"""

    # build.sh

    # slurm.job

    # NEMS.x


    # nems model_configure   

    ocn_pet_num = 0; atm_pet_num = 0; wav_pet_num = 0; nwm_pet_num = 0

    # prepare nems.configure
    dc2={}
    dc2.update({'c'  :'#' })
    try:
      if 'ocn_name' in dic:
        dc2.update({'_ocn_model_': dic['ocn_name']})

      if 'ocn_petlist' in dic:
        dc2.update({'_ocn_petlist_bounds_': dic['ocn_petlist']})
        pet_nums_arr = dic['ocn_petlist'].split()
        ocn_pet_num = int(pet_nums_arr[-1]) - int(pet_nums_arr[0]) + 1 

      if 'coupling_interval_sec' in dic:
        dc2.update({'_coupling_interval_sec_' : dic['coupling_interval_sec']})

      if 'nems_configure' in dic:
        template = os.path.join(env.FIXnsem, 'templates', dic['nems_configure'])
        dest = os.path.join(env.COMIN, 'nems.configure')
        nems_conf = util.tmp2scr(filename=dest, tmpname=template, d=dc2)
        
    except Exception as e:
      print("Error: ",str(e))
      sys.exit(0)

    msg = "\tFinished nems.configure file ...."
    print(util.colory("green",msg))

    
    # prepare model_configure

    total_pets = ocn_pet_num + atm_pet_num + wav_pet_num

    sdate = env.start_date_str
    month=sdate[0:1]; day=sdate[3:4]; year=sdate[6:9]
    hour=sdate[11:12]; minute=sdate[4:5]; second=sdate[17:18] 
    dc={}
    dc.update({'start_year'     :year })
    dc.update({'start_month'    :month })
    dc.update({'start_day'      :day })
    dc.update({'start_hour'     :hour})
    dc.update({'start_minute'   :minute})
    dc.update({'start_second'   :second})
    dc.update({'nhours'         :str(env.frcst_hrs)})
    dc.update({'total_pets'     :str(total_pets)})
    #
    template = os.path.join(env.FIXnsem, 'templates', 'atm_namelist.rc.template')   #TODO check on this file, use model_configure
    dest = os.path.join(env.COMIN, 'model_configure')
    #model_configure  = os.path.join(run_dir,'atm_namelist.rc')
    model_conf = util.tmp2scr(filename=dest, tmpname=template, d=dc)
    #os.system('ln -svf ' + model_configure + ' ' + os.path.join(run_dir,'model_configure' ) )
    #os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/')

    msg = "\tFinished model_configure file ...."
    print(util.colory("green",msg))


    # cp NEMS.x 
    msg = "\tCopying NEMS.x file into %s...." %(env.COMIN)
    print(util.colory("green",msg))
    ##################################################################################


""" Must be adjusted per naming standards """
def prep_ww3(run_dir):
    """
    Prepare ww3 run files
    """
    #ww3
    txt1 = ' > Prepare ww3 inps ... (take couple of minutes)'
    logf(txt1,log_file)

    os.chdir(run_dir)

    # Process WW3 grid and physics
    txt1 = ' > Processing WW3 grid and physics...'
    logf(txt1,log_file)
    os.system('cp -f ' + ww3_grd_inp + '/*.msh ' + run_dir)
    os.system('cp -f ' + ww3_grd_inp + '/ww3_grid.inp ' + run_dir)
    os.system('${EXECnsem}/ww3_grid ww3_grid.inp > ww3_grid.out')
    os.system('cp -p mod_def.ww3 mod_def.inlet')
    os.system('cp -p mod_def.ww3 mod_def.points')

    if base_info.wbound_flg:
       # Process WW3 boundary conditions
       txt1 = ' > Processing WW3 boundary conditions...'
       logf(txt1,log_file)
       os.system('cp -f ${COMINwave}/*.spc ' + run_dir)
       os.system('cp -f ' + ww3_grd_inp + '/ww3_bound.inp ' + run_dir)
       os.system('${EXECnsem}/ww3_bound ww3_bound.inp > ww3_bound.out')
       os.system('mv nest.ww3 nest.inlet')
       os.system('${EXECnsem}/ww3_bound ww3_bound.inp > ww3_bound.out')
       os.system('mv nest.ww3 nest.inlet')  
    ##########
    dc_ww3_multi={}
    dc_ww3_multi.update({'start_pdy'    :base_info.tide_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'end_pdy'      :base_info.wave_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'dt_out_sec'   :3600  })
    ##
    tmpname = os.path.join(FIXnsem, 'templates', base_info.ww3_multi_tmpl)
    ww3_multi = os.path.join(run_dir,'ww3_multi.inp')
    util.tmp2scr(filename=ww3_multi,tmpname=tmpname,d=dc_ww3_multi)
    #os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/') 



""" All input file copying must be communicated to see how we should do them?? """
def prep_adc(dic):

    """
    adcirc preparation per storm and per run name requires:
    1) update model parameter and periodic boundary condition file (fort.15)
       a) copy adcprep executable
    2) copy adc-grd-input (i.e. ocn mesh)
    3) copy wave-grd-input (i.e. wav mesh)
    4) copy restart files, fort.67.nc, fort.68.nc
    5) copy tidefac - for which case?? 
    6) copy adc-input - what and where are these?
    7) pet nums - reason?
    8) copy atm files - which one?, do you need processing?
    9) dependencies: nems model_configure and nems.configure
                     spinup period 
    /scratch2/COASTAL/coastal/save/NAMED_STORMS/NSEM_app_run_workflow
    application_dir = /scratch2/COASTAL/coastal/save/NAMED_STORMS/NSEM_app_run_workflow/ADC-WW3-NWM-NEMS
    app_inp_dir = /scratch2/COASTAL/coastal/save/NAMED_STORMS/NSEM_app_run_workflow/nsemodel_inps
    """
    
    msg = "\tProcessing boundary condition, fort15 ....."
    print(util.colory("green",msg))
    update_fort15(dic)
       

    msg = "\tProcessing ATMesh data ..... "
    print(util.colory("green",msg))

    msg = "\tProcessing adc-wave data ...."
    print(util.colory("green",msg))

    # copy files that are needed 
    adcprep = os.path.join(env.EXECnsem, 'adcprep')
    adc_grd_inp   = os.path.join(env.FIXnsem,'meshes',env.storm,'ocn')  # copy HSOFS grid similar for all cases
    
    """ TODO go through these 
    tidefac   = os.path.join(EXECnsem, 'tidefac')
    # adc_inp   = os.path.join(COMINadc) # this must be copied there manually by HYDRO_STREAM, see CONOPS7
    adc_grd_inp   = os.path.join(FIXnsem,'meshes',storm,'ocn')  # copy HSOFS grid similar for all cases
    ww3_grd_inp   = os.path.join(FIXnsem,'meshes',storm,'wav')
    hot_file = os.path.join(GESIN,'hotfiles','fort.67.nc')  # TODO once manual next after running tide_spinup??
    os.system('cp -f ' + hot_file +' ' + run_dir)
    hot_file = os.path.join(GESIN,'hotfiles','fort.68.nc')        
    os.system('cp -f ' + hot_file +' ' + run_dir)
    """


    # $COMROOT/$NET/$envir/$RUN.$PDY
    target = env.COMINadc
    try:
        msg = "\tCopying files to %s ...." %(target)
        print(util.colory("green",msg))
        shutil.copy(adcprep, target)
    except IOError as e:
        print("\tUnable to copy file. %s" % e)
    except:
        print("\tUnexpected error:", sys.exc_info())

    

""" need clarification to be implemented """
def prep_ww3(wbnd_flg=0):

    """ Prepare ww3 run files """

    # Process WW3 grid and physics
    ww3_grid_inp = os.path.join(env.FIXnsem, "meshes", env.storm, "wav", "ww3_grid.inp")

    os.system('${EXECnsem}/ww3_grid ww3_grid.inp > ww3_grid.out')
    os.system('cp -p mod_def.ww3 mod_def.inlet')
    os.system('cp -p mod_def.ww3 mod_def.points')

    if wbnd_flg:
       # Process WW3 boundary conditions
       # TODO why copy from COMINwave to run_dir??      
       os.system('cp -f ${COMINwave}/*.spc ' + run_dir)
       os.system('cp -f ' + ww3_grd_inp + '/ww3_bound.inp ' + run_dir)
       os.system('${EXECnsem}/ww3_bound ww3_bound.inp > ww3_bound.out')
       os.system('mv nest.ww3 nest.inlet')  

    ##########   TODO Not found, check on these 
    dc_ww3_multi={}
    dc_ww3_multi.update({'start_pdy'    :base_info.tide_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'end_pdy'      :base_info.wave_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'dt_out_sec'   :3600  })
    #
    tmpname = os.path.join(FIXnsem, 'templates', base_info.ww3_multi_tmpl)
    ww3_multi = os.path.join(run_dir,'ww3_multi.inp')
    util.tmp2scr(filename=ww3_multi,tmpname=tmpname,d=dc_ww3_multi)
    #os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/') 




""" nothing in prep needs to be automated!! direct copy suffices"""
def prep_nwm():
    """
    copy setEnvar.sh, namelist.hrldas, hydro.namelist
    copy model data files
    """
    pass


def back_up_codes():
    print("\nTo be implemented .....")
    pass



def plot_domain_decomp():
    print("\nTo be implemented .....")
    pass
