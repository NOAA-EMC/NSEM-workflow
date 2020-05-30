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

