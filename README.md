# NSEM-workflow

## Overview  
  
This is a workflow developed to perform post-storm assessments for NOAA's COASTAL Act 
using the NEMS/NUOPC/ESMF coupling framework. The coupled model components managed by 
this workflow is ADCIRC, unstructured WAVEWATCH III, and the National Water Model. 
Atmospheric forcing is provided by a data model, reading pre-prepared fields.  
  
## Set up system  
  
After cloning the codebase, set up an environment variable `$NSEMdir` that points to the 
location of the cloned code. The executable folder `$NSEMdir/exec/` should contain the following 
binaries from the NEMS app ADC-WW3-NWM-DATM:  
  
    adcprep  
    tidefac  
    ww3_ounf  
    ww3_grid  
    ww3_bound  
    NEMS.x  
  
In the sub-directories `$NSEMdir/ecf/` and `$NSEMdir/jobs/`, set up the location of the scratch space to run 
the application in the following root environment variables:  
  
    $DATAROOT  
    $GESROOT  
    $COMROOT  
  
## Perform a post-storm assessment  
   
a) Change directory to the ecFLow scripts:
  
    $ cd $NSEMdir/ecf  

b) Set the storm for which to perform the assessment, e.g.:  

    $ setenv STORM shinnecock  
   
c) For this storm, first perform the tidal spinup with ADCIRC, starting with a prep step. For this we use 
a specialized prep job in which `RUN_TYPE` is set to `tide_spinup`:  

    $ sbatch jnsem_prep_spinup.ecf  
  
d) Once to inputs are prepared, execute the specialized spinup forecast job, in which `RUN_TYPE` is set to `tide_spinup`:   

    $ sbatch jnsem_forecast_spinup.ecf  
  
e) The previous step will produce hotstart (restart) files of the spun-up model in the directory 
${GESROOT}/para/nsem.${PDY}/${STORM}/hotfiles. Now the full forecast run sequence can be carried out. Start by specifying
the coupled model configuration using the environment variable `RUN_TYPE`, e.g.:

    $ setenv RUN_TYPE atm2wav2ocn  

Currently the following `RUN_TYPE` options are supported:  

    'tide_baserun'        # Tide-only forecast run with ADCIRC
    'best_track2ocn'      # Best-track ATMdata used to force live ADCIRC  
    'wav&best_track2ocn'  # Best-track ATMdata and WAVdata used to force live ADCIRC  
    'atm2ocn'             # ATMdata used to force live ADCIRC  
    'wav2ocn'             # WAVdata used to force live ADCIRC  
    'atm&wav2ocn'         # ATMdata and WAVdata used to force live ADCIRC  
    'atm2wav2ocn'         # ATMdata used to force live ADCIRC and WW3   

f) Now sequentially run the prep, forecast and post jobs that comprise the complete coupled model run for the selected `RUN_TYPE`:

    $ sbatch jnsem_prep.ecf  
    $ sbatch jnsem_forecast.ecf  
    $ sbatch jnsem_post.ecf  
   
g) The working directory of these runs is located in the scratch space:   
   
    ${DATAROOT}/${STORM}.${RUN_TYPE}.${PDY}  
   
h) The model output (after running the post job) are located in the scratch space under:  
   
    ${COMROOT}/nsem/para/${STORM}.${RUN_TYPE}.${PDY}  
   
i) The restart files for subsequent runs are located in the scratch space under:  
   
    ${GESROOT}/para/nsem.${PDY}/${STORM}  

## Disclaimer  
  
The United States Department of Commerce (DOC) GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
   
