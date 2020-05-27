#!/bin/bash
echo "=== In run_nems.sh ==="
#
cd ${RUNdir}

echo "Running NEMS.x..."
srun ./NEMS.x

echo "Copying restart files to GESOUT..."
mkdir ${GESOUT}/hotfiles
cp -p fort.67.nc ${GESOUT}/hotfiles/
cp -p fort.68.nc ${GESOUT}/hotfiles/
