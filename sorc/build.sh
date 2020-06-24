#!/bin/bash

# Description : Script to compile NSEModel NEMS application
# Date        : Jun. 24, 2020

# Developer   : beheen.m.trimble@noaa.gov
# Contributors: saeed.moghimi@noaa.gov
#               andre.vanderwesthuysen@noaa.gov
#               ali.abdolali@noaa.gov


# load modules
source modulefiles/hera/ESMF_NUOPC   

cd NEMS

#clean up
make -f GNUmakefile distclean_ATM COMPONENTS="ATM"
make -f GNUmakefile distclean_OCN COMPONENTS="OCN"
make -f GNUmakefile distclean_WAV COMPONENTS="WAV"
make -f GNUmakefile distclean_NWM COMPONENTS="NWM"
make -f GNUmakefile distclean_NEMS COMPONENTS="NEMS"

#make
make -f GNUmakefile build COMPONENTS="ATM OCN WAV NWM"
