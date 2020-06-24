#!/usr/bin/env python

# stdandard libs
import logging

# third party libs

# user defined libs
import nsem_env as env
import nsem_utils as util
import nsem_prep as prep


logger = logging.getLogger(env.jlogfile)

def setvars(tide_spin_sdate, nems_sdate, tide_spin_edate, nems_edate):
    # To prepare a clod start ADCIRC-Only run for spining-up the tide 
    dic = {

      'Ver': 'v2.0',
      'RunName': 'ocn_spinup_' + env.storm,

      # inp files
      'fetch_hot_from': None,
      'fort15_temp': 'fort.15.template.tide_spinup',

      # time
      'start_date': tide_spin_sdate,
      'start_date_nems': nems_sdate,
      'end_date': tide_spin_edate,
      'dt': 2.0,
      'ndays':  (tide_spin_edate - tide_spin_sdate).total_seconds() / 86400.,   # duration in days

      # fort15 op
      'ndays_ramp': 5,
      'nws': 0,         # no wave no atm
      'ihot': 0,        # no hot start
      'hot_ndt_out': (tide_spin_edate - tide_spin_sdate).total_seconds() / 86400. * 86400 /2.0,

      # NEMS settings
      'nems_configure': 'nems.configure.ocn.IN',
      'model_configure': 'atm_namelist.rc.template',
      'ocn_name': 'adcirc',
      'ocn_petlist': '0 383',
      'coupling_interval_sec': 3600
    }


    msg = """\nStart spinup tide: {}
End spinup tide  : {}
Spinup duration(days): {} 
Hotstart output time(days): {}
Start forecast date: {}
End forecast date  : {}""".format(dic['start_date'], dic['end_date'], dic['ndays'],
                                  dic['hot_ndt_out'], nems_sdate, nems_edate)

    print(msg)

    return dic




def main():

    msg = "\n%s: Setting up %s for storm %s .........." %(__file__, env.run, env.storm)
    print(util.colory("blue", msg))

    msg = "\nCalculating spinup time ....."
    print(util.colory("red", msg))
    tide_spin_sdate,tide_spin_edate, _, _, nems_sdate, nems_edate, = prep.spinup_time()

    # To prepare a clod start ADCIRC-Only run for spining-up the tide 
    msg = "\nSetting model variables ....."
    print(util.colory("red", msg))
    dic = setvars(tide_spin_sdate,tide_spin_edate,nems_sdate,nems_edate) 

    msg = "\nPreprocessing ADCIRC model files ....."
    print(util.colory("red", msg))
    prep.prep_adc(dic)

    msg = "\nPreparing NEMS configuration files ....."
    print(util.colory("red", msg))
    prep.prep_nems(dic)

    msg = "\nStart running model for %s\n" %(env.run)
    print(util.colory("red", msg))
    # add the run portion

    msg = "\nFinished the model run .....\n"
    print(util.colory("blue", msg))


 

if __name__ == '__main__':

    main()

