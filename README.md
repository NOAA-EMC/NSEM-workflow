# NSEM-workflow

1. Overview  
  
This is a workflow developed to perform post-storm assessments for NOAA's COASTAL Act 
using the NEMS/NUOPC/ESMF coupling framework. The coupled model components managed by 
this workflow is ADCIRC, unstructured WAVEWATCH III, and the National Water Model. 
Atmospheric forcing is provided by a data model, reading pre-prepared fields.  
  
2. Set up system  
  
After cloning the codebase, set up an environment variable $NSEMdir that points to the 
location of the cloned code. The executable folder $NSEMdir/exec/ should contain the following 
binaries from the NEMS app ADC-WW3-NWM-DATM:  
  
&nbsp;adcprep  
&nbsp;tidefac  
&nbsp;ww3_ounf  
&nbsp;ww3_grid  
&nbsp;ww3_bound  
&nbsp;NEMS.x  
  
In the sub-directories $NSEMdir/ecf/ and $NSEMdir/jobs/, set up the location of the scratch space to run 
the application in the following root environment variables:  
  
   $DATA  
   $GESROOT  
   $COMROOT  
  
3. Perform a post-storm assessment  
  
a) Set the storm for which to perform the assessment:  

   $ setenv STORM shinnecock  
  
b) Set the type of model run:  

   $ setenv RUN_TYPE tide_spinup  
  
c) Run the prep, forecast and post jobs that comprises the complete model run:

   $ sbatch jnsem_prep.ecf  
   $ sbatch jnsem_forecast.ecf  
   $ sbatch jnsem_post.ecf  

d) Repeat steps (c) as needed to perform the tidal spinup and subsequently the coupled 
model run. For example, a typical sequence is:

   $ setenv RUN_TYPE tide_spinup  
   $ sbatch jnsem_prep.ecf  
   $ sbatch jnsem_forecast.ecf  
   $ sbatch jnsem_post.ecf  

   $ setenv RUN_TYPE atm2wav2ocn  
   $ sbatch jnsem_prep.ecf  
   $ sbatch jnsem_forecast.ecf  
   $ sbatch jnsem_post.ecf  
   
e) The results of these working directory of these runs are located in the scratch space:   
   
   ${STORM}.${RUN_TYPE}.${PDY}  
   
f) The model output (after running the post job) are located in the scratch space under:  
   
   ${COMROOT}/nsem/para/${STORM}.${RUN_TYPE}.${PDY}  
   
g) The restart files for subsequent runs are located in the scratch space under:  
   
   ${GESROOT}/para/nsem.${PDY}/${STORM}  
   
