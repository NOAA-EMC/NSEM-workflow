# ----------------------------------------------------------- 
# Python Script File
# Tested Operating System(s): RHEL 7, Python 3.7.5
# Tested Run Level(s): 
# Shell Used: BASH shell
# Original Author(s): Saeed Moghimi
# File Creation Date: 05/15/2020
# Date Last Modified:
#
# Version control: 1.00
#
# Support Team:
#
# Contributors: Andre van der Westhuysen
#
# ----------------------------------------------------------- 
# ------------- Program Description and Details ------------- 
# ----------------------------------------------------------- 
#
# Python utility module
#
# -----------------------------------------------------------

from string import Template

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

