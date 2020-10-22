#!/bin/bash
# --------------------------------------------------------------------------- #
#                                                                             #
# Copy external fix files and binaries needed for build process and running   #
#                                                                             #
# Last Changed : 10-22-2020                                     October 2020  #
# --------------------------------------------------------------------------- #

if [ "${NSEMdir}" == "" ]
    then 
    echo "ERROR - Your NSEMdir variable is not set"
    exit 1
fi

echo 'Fetching externals...'
cp -rp /scratch2/COASTAL/coastal/save/NSEM-workflow-externals/fix/meshes/* ${NSEMdir}/fix/meshes/

