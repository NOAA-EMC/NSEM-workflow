# ----------------------------------------------------------- 
# Python Script File
# Shell Used: BASH shell
# Original Author(s): Saeed Moghimi
# File Creation Date: 05/15/2020
# Date Last Modified: 06/15/2020
#
# Version control: 1.00
#
# Support Team: Beheen Trimble
#
# Contributors: Andre van der Westhuysen
#               Ali Abdolali
# ----------------------------------------------------------- 
# ------------- Program Description and Details ------------- 
# ----------------------------------------------------------- 
#
# Python utility module
#
# -----------------------------------------------------------

from string import Template

# local libs
from color import Color, Formatting, Base, ANSI_Compatible



def colory(which, text):
     msg = ""
     if which.lower() == "red" :
         msg = Color.F_Red + text
     elif which.lower() == "green" :
         msg = Color.F_Green + text
     elif which.lower() == "blue" :
         msg = Color.F_Blue + text
     msg += Color.F_Default
     return msg


def tmp2scr(filename=None,tmpname=None,d=None):
    """
    Replace a pattern in tempelate file and generate a new input file.
    filename: full path to input file
    tmpname:  full path to tempelate file
    d:        dictionary of all patterns need to replace   

    Uses string.Template from the Python standard library
    """
    fileout = open( filename,'w' )
    filetmp = open( tmpname ,'r' )
    out = Template( filetmp.read() ).safe_substitute(d)
    fileout.write(str(out))
    fileout.close()
    filetmp.close()
    return out   # just-incase if needed 


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

