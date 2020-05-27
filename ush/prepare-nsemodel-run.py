
__author__ = "Saeed Moghimi"
__copyright__ = "Copyright 2019, NOAA"
__license__ = "GPL"
__version__ = "1.1"
__email__ = "moghimis@gmail.com"

import numpy as np
import os, sys
from datetime import timedelta
import time
from dateutil.parser import parser
from string import Template

# Get enviroment vars from ecFlow scripting
RUNdir = os.getenv('RUNdir')
EXECnsem = os.getenv('EXECnsem')
PARMnsem = os.getenv('PARMnsem')
FIXnsem = os.getenv('FIXnsem')
GESIN = os.getenv('GESIN')
COMINatm = os.getenv('COMINatm')
COMINwave = os.getenv('COMINwave')
COMINwavdata = os.getenv('COMINwavdata')
COMINadc = os.getenv('COMINadc')
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
##########################################
#global vars
start_date = base_info.start_date
duration   = timedelta (days = base_info.ndays)
end_date   = start_date + duration

print('Storm case: '+STORM)
print('Run type: '+RUN_TYPE)
print('start_date:')
print(start_date)
print('duration:')
print(duration)
print('end_date:')
print(end_date)

#def_files
#adcprep
adcprep   = os.path.join(EXECnsem, 'adcprep')
tidefac   = os.path.join(EXECnsem, 'tidefac')
adc_inp   = os.path.join(COMINadc)
adc_grd_inp   = os.path.join(FIXnsem,'meshes',base_info.mesh,'ocn')
ww3_grd_inp   = os.path.join(FIXnsem,'meshes',base_info.mesh,'wav')

#modfile   = os.path.join(base_info.application_dir, base_info.module_file )
nems_exe  = os.path.join(EXECnsem, 'NEMS.x')

global log_file,run_dir

## functions
def logf(txt1,log_file):
    os.system('echo "'+ txt1+ '" >> '+ log_file )
    os.system('echo "'+ txt1+ '"')

#def tmp2scr(filename,tmpname,d):
#    """
#    Replace a pattern in tempelate file and generate a new input file.
#    filename: full path to input file
#    tmpname:  full path to tempelate file
#    d:        dictionary of all patterns need to replace
#    
#    Dependency Cheetah    
#    """
#        
#    from Cheetah.Template import Template
#    #print filename
#    fileout = open( filename,'w' )
#    filetmp = open( tmpname ,'r' )
#    out     = Template(file=filetmp,searchList =[d])
#    fileout.write(str(out))
#    fileout.close()
#    filetmp.close()

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
###########################################
def get_run_scr():
    # run dir setting 
    curr_time  = time.strftime("%Y%m%d_h%H_m%M_s%S")
    run_scr    = os.path.join(RUNdir, base_info.RunName+'_'+base_info.Ver+'_' + curr_time + '.sh' )
    log_file    = os.path.join(RUNdir, base_info.RunName+'_'+base_info.Ver+'_' + curr_time + '.log' )
    os.system('touch  ' + run_scr)
    return run_scr,log_file

def get_run_dir():
    # run dir setting 
    curr_time  = time.strftime("%Y%m%d_h%H_m%M_s%S")
    run_dir    =  os.path.join(base_info.main_run_dir,base_info.RunName+'_'+base_info.Ver,'rt_' + curr_time + \
        'r' +str(int(np.random.rand(1)*1000+1000))[1:] )
    os.system('mkdir -p ' + run_dir)
    #print ' > Run dir .. \n ',run_dir
    txt1 = ' > Run dir = ' + run_dir
    logf(txt1,log_file)
    # backup script
    os.system('mkdir -p '+ run_dir+'/scr/')
    #Back_up scr
    args     = sys.argv
    scr_name = args[0]    
    scr_dir  = os.getcwd()
    os.system('cp -fr  '+scr_dir+'/'+scr_name +'    '+run_dir+'/scr/')
    os.system('cp -fr  base_info*                   '+run_dir+'/scr/')
    #
    return run_dir

def prep_adc(run_dir):
    """
    Prepare adcirc run files
    uses vars imported from base_info.py
   
    """
    #adcirc
    #print ' > Prepare adcirc inps ... (take couple of minutes)'
    txt1 = ' > Prepare adcirc inps ... (take couple of minutes)'
    logf(txt1,log_file)    
    
    # copy HSOFS grid similar for all cases
    os.system('cp -f ' + adc_grd_inp + '/*.*   ' + run_dir)    

    #Prepare fort.15
    adcirc_start_date = start_date.isoformat().replace('T',' ')+ ' UTC'

    txt1 = '   > Prepare fort.15 ..'
    logf(txt1,log_file)   

    d15 = {}
    d15.update({'start_date'    :adcirc_start_date          })
    d15.update({'run_time_days' :str(base_info.ndays)  })

    d15.update({'dramp'         :str(base_info.ndays_ramp)  })
    d15.update({'nws'           :str(base_info.nws)  })
    d15.update({'ihot'          :str(base_info.ihot)  })
    d15.update({'dt'            :str(base_info.dt)  })
    d15.update({'hot_ndt_out'   :str(base_info.hot_ndt_out)  })
    
    if base_info.nws > 0:
        d15.update({'WTIMINC'       :str(base_info.WTIMINC)  })
        d15.update({'RSTIMINC'      :str(base_info.RSTIMINC)  })
        #os.system('cp -f ' + adc_inp + '/fort* ' + run_dir)
        #os.system('cp -f ' + adc_inp + '/*.sh  ' + run_dir)
        #os.system('cp -f ' + adc_inp + '/*.py  ' + run_dir)
        os.system ('cp -f ' + adc_inp + '/*.*   ' + run_dir)   
  
    # get tide facts
    d15_tide = get_tidal_fact(run_dir)
    d15.update(d15_tide)
    # get updated fort.15
    fort15tmp = os.path.join(adc_grd_inp,base_info.fort15_temp)
    fort15  = os.path.join(run_dir,'fort.15')
    tmp2scr(filename=fort15,tmpname=fort15tmp,d=d15)
    os.system('cp -fr  ' +   fort15tmp          +'  '   +run_dir+'/scr/')
    
    #print ' > AdcPrep ... '
    txt1 = ' > AdcPrep ...  '
    logf(txt1,log_file) 
    pet_nums = np.int_ (np.array(base_info.ocn_petlist.split()))
    adc_pet_num = pet_nums[-1] - pet_nums[0] + 1 

    #comm0 = "source " + modfile +' ; '
    comm1  = ' cd   ' + run_dir + ' ; '+adcprep +' --np '+ str(adc_pet_num)+'  --partmesh >  adcprep.log'
    print(comm1)
    os.system(comm1)
    #
    comm2 = ' cd ' + run_dir + ' ; '+adcprep +' --np '+ str(adc_pet_num)+'  --prepall  >> adcprep.log'
    #print(comm2)
    txt1 = comm2
    logf(txt1,log_file) 
    os.system(comm2)
    
    txt1 = ' > End of Preproc.x ...  '
    logf(txt1,log_file)
    """
    # Treat hotfile
    try:
        GESIN
    except NameError:
        GESIN = None

    if GESIN is not None:
        #print ' > Copy HotStart input file from >', base_info.fetch_hot_from
    """
    txt1 = ' > Copy HotStart input file from >  '+ GESIN
    logf(txt1,log_file) 
        
    hot_file = os.path.join(GESIN,'hotfiles','fort.67.nc')
    os.system('cp -f ' + hot_file +' ' + run_dir)
    hot_file = os.path.join(GESIN,'hotfiles','fort.68.nc')        
    os.system('cp -f ' + hot_file +' ' + run_dir)

#def prep_atm():
#    print ' > Prepare ' + base_info.atm_name
#    #os.system ('cp -r  '+  os.path.join(base_info.app_inp_dir,base_info.atm_inp_dir)  + '  ' + run_dir)
    
    
    
    #TODO: Only copy the forcing file not the whole directory
    
#def prep_wav():
#    print ' > Prepare ' + base_info.wav_name
#    os.system ('cp -r  '+  os.path.join(base_info.app_inp_dir,base_info.wav_inp_dir)  + '  ' + run_dir)

def prep_ww3(run_dir):
    """
    Prepare ww3 run files
    uses vars imported from base_info.py
   
    """
    #ww3
    txt1 = ' > Prepare ww3 inps ... (take couple of minutes)'
    logf(txt1,log_file) 

    os.chdir(run_dir)

    # Process WW3 grid and physics
    print("Processing WW3 grid and physics...")
    os.system('cp -f ' + ww3_grd_inp + '/*.msh ' + run_dir)
    os.system('cp -f ' + ww3_grd_inp + '/ww3_grid.inp ' + run_dir)
    os.system('${EXECnsem}/ww3_grid ww3_grid.inp > ww3_grid.out')
    os.system('cp -p mod_def.ww3 mod_def.inlet')
    os.system('cp -p mod_def.ww3 mod_def.points')

    if base_info.wbound_flg:
       # Process WW3 boundary conditions
       print("Processing WW3 boundary conditions...")
       os.system('cp -f ${COMINwave}/*.spc ' + run_dir)
       os.system('cp -f ' + ww3_grd_inp + '/ww3_bound.inp ' + run_dir)
       os.system('${EXECnsem}/ww3_bound ww3_bound.inp > ww3_bound.out')
       os.system('mv nest.ww3 nest.inlet')  
    ##########
    #start_pdy = datetime.datetime(base_info.start_date_nems.year, \
    #                              base_info.start_date_nems.month, \
    #                              base_info.start_date_nems.day, \
    #                              base_info.start_date_nems.hour, \
    #                              base_info.start_date_nems.minute, \
    #                              base_info.start_date_nems.second)
    #end_pdy = start_pdy + datetime.timedelta(days=base_info.ndays)
    #start_pdy_string = start_pdy.strftime("%Y%m%d %H%M%S")
    #end_pdy_string = base_info.wave_spin_end_date.strftime("%Y%m%d %H%M%S")
    dc_ww3_multi={}
    dc_ww3_multi.update({'start_pdy'    :base_info.tide_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'end_pdy'      :base_info.wave_spin_end_date.strftime("%Y%m%d %H%M%S") })
    dc_ww3_multi.update({'dt_out_sec'   :3600  })
    ##
    tmpname = os.path.join(FIXnsem, 'templates', base_info.ww3_multi_tmpl)
    ww3_multi = os.path.join(run_dir,'ww3_multi.inp')
    tmp2scr(filename=ww3_multi,tmpname=tmpname,d=dc_ww3_multi)
    os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/') 

def prep_nems(run_dir):
    """
    Preapre nems run files 
    uses vars imported from base_info.py
    
    
    """
    #print ' > Prepare NEMS related input files ..'
    txt1 = ' > Prepare NEMS related input files ..'
    logf(txt1,log_file)     
    # NEMS.x
    os.system ('cp -f ' + nems_exe + ' ' + run_dir)    

    #   
    ocn_pet_num = 0
    atm_pet_num = 0
    wav_pet_num = 0

    dc2={}
    dc2.update({'c'  :'#' })
    if base_info.ocn_name is not None:
        dc2.update({'_ocn_model_'          : base_info.ocn_name    })
        dc2.update({'_ocn_petlist_bounds_' : base_info.ocn_petlist })
        pet_nums = np.int_ (np.array(base_info.ocn_petlist.split()))
        ocn_pet_num = pet_nums[-1] - pet_nums[0] + 1 

    if base_info.atm_name is not None:
        dc2.update({'_atm_model_'          : base_info.atm_name    })
        dc2.update({'_atm_petlist_bounds_' : base_info.atm_petlist })
        pet_nums = np.int_ (np.array(base_info.atm_petlist.split()))
        atm_pet_num = pet_nums[-1] - pet_nums[0] + 1 

    if base_info.wav_name is not None:
        dc2.update({'_wav_model_'          : base_info.wav_name    })
        dc2.update({'_wav_petlist_bounds_' : base_info.wav_petlist })
        pet_nums = np.int_ (np.array(base_info.wav_petlist.split()))
        wav_pet_num = pet_nums[-1] - pet_nums[0] + 1 

    if base_info.coupling_interval_sec is not None:
        dc2.update({'_coupling_interval_sec_' : base_info.coupling_interval_sec    })

    #if base_info.coupling_interval_slow_sec is not None:
    #    dc2.update({'_coupling_interval_slow_sec_' : base_info.coupling_interval_slow_sec    })

    #if base_info.coupling_interval_fast_sec is not None:
    #    dc2.update({'_coupling_interval_fast_sec_' : base_info.coupling_interval_fast_sec    })

    txt1 = '   > Prepare atm_namelist.rc ..'
    logf(txt1,log_file)   
    
    total_pets = ocn_pet_num + atm_pet_num + wav_pet_num
    tmpname = os.path.join(PARMnsem, base_info.nems_configure)
    model_configure  = os.path.join(run_dir,'nems.configure')
    tmp2scr(filename=model_configure,tmpname=tmpname,d=dc2)
    os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/')
    ##########
    dc={}
    dc.update({'start_year'     :base_info.start_date_nems.year    })
    dc.update({'start_month'    :base_info.start_date_nems.month   })
    dc.update({'start_day'      :base_info.start_date_nems.day     })
    dc.update({'start_hour'     :base_info.start_date_nems.hour    })
    dc.update({'start_minute'   :base_info.start_date_nems.minute  })
    dc.update({'start_second'   :base_info.start_date_nems.second  })
    dc.update({'nhours'         :str(base_info.ndays * 24)})
    dc.update({'total_pets'     :str(total_pets)})
    ##
    tmpname = os.path.join(FIXnsem, 'templates', base_info.model_configure)
    model_configure  = os.path.join(run_dir,'atm_namelist.rc')
    tmp2scr(filename=model_configure,tmpname=tmpname,d=dc)
    os.system('ln -svf ' + model_configure + ' ' + os.path.join(run_dir,'model_configure' ) )
    os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/')
    ##################################################################################
    txt1 = '   > Prepare nems.configure ..'
    logf(txt1,log_file)   
    
    pet_max = 0
    dc3={}
    dc3.update({'c'  :'#' })
    if base_info.ocn_name is not None:
        dc3.update({'_ocn_model_'          : base_info.ocn_name    })
        dc3.update({'_ocn_petlist_bounds_' : base_info.ocn_petlist })
        pet_nums = np.int_ (np.array(base_info.ocn_petlist.split()))
        ocn_pet_num = pet_nums[-1] - pet_nums[0] + 1 
        pet_max = max(pet_nums[0],pet_nums[-1])

    if base_info.atm_name is not None:
        dc3.update({'_atm_model_'          : base_info.atm_name    })
        dc3.update({'_atm_petlist_bounds_' : base_info.atm_petlist })
        pet_nums = np.int_ (np.array(base_info.atm_petlist.split()))
        atm_pet_num = pet_nums[-1] - pet_nums[0] + 1 
        pet_max = max(pet_max,pet_nums[0],pet_nums[-1])

    if base_info.wav_name is not None:
        dc3.update({'_wav_model_'          : base_info.wav_name    })
        dc3.update({'_wav_petlist_bounds_' : base_info.wav_petlist })
        pet_nums = np.int_ (np.array(base_info.wav_petlist.split()))
        wav_pet_num = pet_nums[-1] - pet_nums[0] + 1 
        pet_max = max(pet_max,pet_nums[0],pet_nums[-1])

    if base_info.coupling_interval_sec is not None:
        dc3.update({'_coupling_interval_sec_' : base_info.coupling_interval_sec    })

    #if base_info.coupling_interval_slow_sec is not None:
    #    dc3.update({'_coupling_interval_slow_sec_' : base_info.coupling_interval_slow_sec    })

    #if base_info.coupling_interval_fast_sec is not None:
    #    dc3.update({'_coupling_interval_fast_sec_' : base_info.coupling_interval_fast_sec    })

    #total_pets = ocn_pet_num + atm_pet_num + wav_pet_num
    total_pets = pet_max + 1
    tmpname = os.path.join(PARMnsem, base_info.nems_configure)
    model_configure  = os.path.join(run_dir,'nems.configure')
    tmp2scr(filename=model_configure,tmpname=tmpname,d=dc3)
    os.system('cp -fr  ' +   tmpname          +'  '   +run_dir+'/scr/')

    txt1 = '   > Prepare config.rc ..'
    logf(txt1,log_file)   
    
    #generate apps.rc file
    apps_conf = os.path.join(run_dir,'config.rc')
    
    if base_info.wav_name == 'ww3data':
        #wav_dir   = os.path.join(run_dir, os.path.normpath(base_info.wav_inp_dir).split('/')[-1])
        wav_dir = COMINwave
        os.system ('echo " wav_dir: ' +  wav_dir                        + ' " >> ' + apps_conf )
        os.system ('echo " wav_nam: ' +  base_info.wav_netcdf_file_name + ' " >> ' + apps_conf )
        #
        wav_inp_file    = os.path.join(COMINwave,base_info.wav_netcdf_file_name)
        wav_rundir_file = os.path.join(wav_dir,base_info.wav_netcdf_file_name)
        if True:
            txt1 =  '  > Link Wave Inp ...'
            logf(txt1,log_file)             
            
            os.system ('mkdir -p  ' +  wav_dir                                   )
            os.system ('ln    -sf ' +  wav_inp_file + ' ' + wav_rundir_file      )
        else:        
            #print '  > Copy Wave Inp ...'
            txt1 = '  > Copy WAV Inp ...'
            logf(txt1,log_file)             
            
            os.system ('mkdir -p  ' +  wav_dir                                   )
            os.system ('cp    -f  ' +  wav_inp_file + ' ' + wav_rundir_file      )

    if base_info.atm_name is not None:
        #atm_dir   = os.path.join(run_dir, os.path.normpath(base_info.atm_inp_dir).split('/')[-1])
        atm_dir = COMINatm
        os.system ('echo " atm_dir: ' +  atm_dir                        + ' " >> ' + apps_conf )
        os.system ('echo " atm_nam: ' +  base_info.atm_netcdf_file_name + ' " >> ' + apps_conf )
        #
        atm_inp_file    = os.path.join(COMINatm,base_info.atm_netcdf_file_name)
        atm_rundir_file = os.path.join(atm_dir,base_info.atm_netcdf_file_name)
        if True:
            txt1 =  '  > Link ATM Inp ...'
            logf(txt1,log_file)             
            
            os.system ('mkdir -p  ' +  atm_dir                                   )
            os.system ('ln    -sf ' +  atm_inp_file + ' ' + atm_rundir_file      )
        else:
            #print '  > Copy ATM Inp ...'  
            txt1 = '  > Copy ATM Inp ...'
            logf(txt1,log_file)                  
            os.system ('mkdir -p  ' +  atm_dir                                   )
            os.system ('cp    -f  ' +  atm_inp_file + ' ' + atm_rundir_file      )               
    
"""    
    txt1 = '   > Prepare qsub.sh  ..'
    logf(txt1,log_file)   
    
    #prepare run scr
    qsub       = os.path.join(run_dir,'slurm.sh')
    #
    dr={}
    #dr.update({'modfile'  :modfile   })
    dr.update({'NumProc'  :str(total_pets)  })
    dr.update({'WallTime' :base_info.WallTime      })
    dr.update({'Queue'    :base_info.Queue         })
    dr.update({'RunName'  :(base_info.RunName+base_info.Ver) })
    #tmp2scr(filename=qsub ,tmpname='qsub.template',d=dr)
    tmp2scr(filename=qsub ,tmpname=base_info.qsub_tempelate,d=dr)
    
    os.system('cp -fr '+ base_info.qsub_tempelate +' ' +run_dir+'/scr/')
    os.system('cp -fr   run*.sh           '            +run_dir)
"""

def get_tidal_fact(run_dir):
    """
    based on spin-up start time prepare tide fac to be used in fort.15.tempelate
    In:
    Out: tidal fact dictionary
    
    """
    txt1 = '   > Prepare Tidal factors ..'
    logf(txt1,log_file)       
    
    duration = str ((base_info.wave_spin_end_date-base_info.tide_spin_start_date).total_seconds() /86400.)
    

    # copy tidal input file
    os.system('cp -f ' + PARMnsem + '/storms/' + STORM + '/tide_inp.txt ' + run_dir)

    tidefac_inp_file = os.path.join(run_dir, 'tide_inp.txt')
    tidefac_inp      = open(tidefac_inp_file,'w')
    # write data
    tidefac_inp.write( duration + ' \n')  #for 1 year
    tidefac_inp.write(str(base_info.tide_spin_start_date.hour) +' ')
    tidefac_inp.write(str(base_info.tide_spin_start_date.day)  +' ')
    tidefac_inp.write(str(base_info.tide_spin_start_date.month)+' ')
    tidefac_inp.write(str(base_info.tide_spin_start_date.year) +' ')
    tidefac_inp.close()
       
    #comm0 = "source " + modfile +' ; '
    comm1  = ' cd   ' + run_dir + ' ; '+tidefac +' <  tide_inp.txt  >  tidefac.log'
    #print(comm1)
    
    txt1 = comm1
    logf(txt1,log_file)      
    
    os.system(comm1)
    
    tidefac_dic = {}
    tidefac_out_file = os.path.join(run_dir, 'tide_fac.out')
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
                  fft13=fft13,facet13=facet13) 

def replace_pattern_line(filename, pattern, line2replace):
    """
    replace the whole line if the pattern found
    
    """
    
    tmpfile = filename+'.tmp2'
    os.system(' cp  -f ' + filename + '  ' + tmpfile)
    tmp  = open(tmpfile,'r')
    fil  = open(filename,'w')
    for line in tmp:
        fil.write(line2replace if pattern in line else line)
        
    tmp.close()
    fil.close()
    os.system('rm ' + tmpfile  )  

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
   
def back_up_codes(run_dir):
    #cap_dir  = os.path.join(base_info.application_dir, 'ADCIRC_CAP' )        
    ocn_dir  = os.path.join(base_info.application_dir, 'ADCIRC' )            
    nem_dir  = os.path.join(base_info.application_dir, 'NEMS' )            
    #   
    #os.system('tar -zcf '+run_dir+'/scr/ADCIRC_CAP.tgz '+ cap_dir)
    os.system('tar -zcf '+run_dir+'/scr/ADCIRC.tgz '    + ocn_dir)
    os.system('tar -zcf '+run_dir+'/scr/NEMS.tgz '      + nem_dir)
    #print ' > Finished backing up codes'

    txt1 = ' > Finished backing up codes ..'
    logf(txt1,log_file)      

def plot_domain_decomp(run_dir):
    import pynmd.models.adcirc.post as adcp 
    import pynmd.plotting.plot_settings as ps
    import matplotlib.pyplot as plt
    decomps = adcp.ReadFort80(run_dir+'/')
    nproc = decomps['nproc']
    IMAP_NOD_LG = decomps['IMAP_NOD_LG'] 
    IMAP_EL_LG  = decomps['IMAP_EL_LG'] 
    IMAP_NOD_GL = decomps['IMAP_NOD_GL']
    x,y,tri = adcp.ReadTri  (run_dir+'/')
     
    fig = plt.figure(figsize=(5,5))
    ax  =  fig.add_subplot(111)
    xp  = []
    yp  = []
    cc = 100 * ps.colors
    mm = 100 * ps.marker
    for ip in range(nproc):
        ind = np.where(IMAP_NOD_GL[:,1] == ip)
        ind = ind[::10]
        ax.scatter(tri.x[ind],tri.y[ind], c = cc[ip],
            s = 0.2 , edgecolors = 'None', marker = mm[ip])
    fig.savefig(run_dir + '/0decomp.png',dpi=450)
    plt.close()
    #print ' > Finished plotting domain decomposition'
    txt1 = ' > Finished plotting domain decomposition ..'
    logf(txt1,log_file)          
########
def main0():
    prep_adc()

    #if base_info.atm_name is not None:
    #    prep_atm()
    # 
    #if base_info.wav_name is not None:
    #    prep_wav()

    prep_nems()
    #change_nws() No need for this any more
    
    back_up_codes()
    
    #plot_domain_decomp()

def one_run_eq(run_scr):
    #run_dir =  get_run_dir()
    run_dir = RUNdir
    os.system('echo "cd  ' + run_dir +' " >> ' + run_scr )
    #os.system('echo "qsub qsub.sh      " >> ' + run_scr )
    os.system('echo "sbatch slurm.sh    " >> ' + run_scr )
    #
    prep_nems(run_dir)
    prep_adc(run_dir)
    if base_info.run_option == 'atm2wav2ocn': 
       prep_ww3(run_dir) 

    if False:
        plot_domain_decomp(run_dir)
        back_up_codes(run_dir)

def main():
    """
    Main loop
    
    """  
    txt1 = ' > Spin-up Start Time:   '   + base_info.tide_spin_start_date.isoformat()
    logf(txt1,log_file)   
 
    txt1 = ' > Base run Start Time:  ' + base_info.tide_spin_end_date.isoformat()
    logf(txt1,log_file)   

    txt1 = ' > End Time:             ' + base_info.wave_spin_end_date.isoformat()
    logf(txt1,log_file)   
  
  
    if (base_info.atm_name is None) and (base_info.wav_name is None):
        #print ' > SpinUp case :'
        txt1 = ' > SpinUp/TideBaseRun/BestTrack case :'
        logf(txt1,log_file)    
        
        one_run_eq(run_scr)
    
    if (base_info.atm_name is not None) and (base_info.wav_name is None):
        #print ' > ATM2OCN for ',len ( base_info.atm_netcdf_file_names), 'cases.'
        txt1 = ' > ATM2OCN for '+ str(len ( base_info.atm_netcdf_file_names))+ ' cases.'
        logf(txt1,log_file)    
         
        for atm_file in base_info.atm_netcdf_file_names:
            base_info.atm_netcdf_file_name = atm_file
            #print '  > ',atm_file
            txt1 = '  > '+ atm_file
            logf(txt1,log_file)                
            
            one_run_eq(run_scr)
            txt1 = '................................................... \n\n'
            logf(txt1,log_file) 
    
    if (base_info.atm_name is None) and (base_info.wav_name is not None):
        #print ' > Wav2OCN for ',len (base_info.wav_netcdf_file_names), 'cases.'
        txt1 = ' > Wav2OCN for '+str(len (base_info.wav_netcdf_file_names))+ ' cases.'
        logf(txt1,log_file) 
         
        for wav_file in base_info.wav_netcdf_file_names:
            base_info.wav_netcdf_file_name = wav_file
            #print '  > ',wav_file
            txt1 = '  > '+ wav_file
            logf(txt1,log_file)             
            one_run_eq(run_scr)
            txt1 = '................................................... \n\n'
            logf(txt1,log_file) 
    
    if (base_info.atm_name is not None) and (base_info.wav_name is not None):
        if (base_info.wav_name == 'ww3data'):
           #print ' > Wav&ATM2OCN for ',len (base_info.wav_netcdf_file_names), 'cases.'
           txt1 = ' > Wav&ATM2OCN for '+str(len (base_info.wav_netcdf_file_names)) + ' cases.'
           logf(txt1,log_file)            
           for ifile in range(len(base_info.atm_netcdf_file_names)):
               base_info.atm_netcdf_file_name = base_info.atm_netcdf_file_names[ifile]
               base_info.wav_netcdf_file_name = base_info.wav_netcdf_file_names[ifile]
               #print '  > ',wav_file
               #print '  > ',atm_file
            
               txt1 = '  WAVFile> '+ base_info.wav_netcdf_file_names[ifile] +\
                      '     ATMFile> ' + base_info.atm_netcdf_file_names[ifile]
               logf(txt1,log_file)  
            
               one_run_eq(run_scr)
               txt1 = '................................................... \n\n'
               logf(txt1,log_file) 

        if (base_info.wav_name == 'ww3'):
           txt1 = ' > Atm2Wav2OCN for '+str(len (base_info.atm_netcdf_file_names)) + ' cases.'
           logf(txt1,log_file)   
         
           for atm_file in base_info.atm_netcdf_file_names:
               base_info.atm_netcdf_file_name = atm_file
               #print '  > ',atm_file
               txt1 = '  > '+ atm_file
               logf(txt1,log_file)                
            
               one_run_eq(run_scr)
               txt1 = '................................................... \n\n'
               logf(txt1,log_file) 

    txt1 = '-----------------------------------'
    logf(txt1,log_file)    
    txt1 = 'FINISH  > Ready to submit ..'
    logf(txt1,log_file)       
    txt1 = '-----------------------------------'
    logf(txt1,log_file)      


if __name__ == '__main__':

    run_scr,log_file = get_run_scr()
    main()

    
    
    
    
"""    
    else:     
        avail_options = [
#                'tide_spinup',
#                'tide_baserun',
                'best_track2ocn',
                'wav&best_track2ocn',
#                'atm2ocn',
#                'wav2ocn',
#                'atm&wav2ocn',    
                ]
    
    
        for run_option in avail_options:
            base_info.run_option = run_option
            main()
"""
