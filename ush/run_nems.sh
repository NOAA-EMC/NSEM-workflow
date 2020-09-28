#!/bin/bash
# ----------------------------------------------------------- 
# UNIX Shell Script File
# Tested Operating System(s): RHEL 7
# Tested Run Level(s): 
# Shell Used: BASH shell
# Original Author(s): Andre van der Westhuysen
# File Creation Date: 05/15/2020
# Date Last Modified:
#
# Version control: 1.00
#
# Support Team:
#
# Contributors: 
#
# ----------------------------------------------------------- 
# ------------- Program Description and Details ------------- 
# ----------------------------------------------------------- 
#
# Script to call NEMS.x executable for forecast run
#
# ----------------------------------------------------------- 

echo "=== In run_nems.sh ==="
#
cd ${RUNdir}

echo "Running NEMS.x..."
#srun -v --slurmd-debug=4 --mem=3000 ./NEMS.x
srun ./NEMS.x

echo "Copying restart files to GESOUT..."
mkdir ${GESOUT}/hotfiles
cp -p fort.67.nc ${GESOUT}/hotfiles/
cp -p fort.68.nc ${GESOUT}/hotfiles/
cp -p restart*.* ${GESOUT}/hotfiles/
