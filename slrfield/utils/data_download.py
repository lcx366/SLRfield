
import numpy as np
from os import path,mkdir,makedirs,remove
from glob import glob
from pathlib import Path
from ftplib import FTP
from datetime import datetime,timedelta
from spacetrack import SpaceTrackClient

from .try_download import tqdm_ftp,tqdm_request

def download_eop(out_days=7,dir_to=None):
    """
    Download or update the Earth Orientation Parameters(EOP) file from IERS.

    Usage: 
    >>> dir_eop = download_eop()

    Parameters: 
    out_days -> [int, optional, default = 7] Update cycle of the EOP file
    dir_to   -> [str, optional, default = None] Directory for storing EOP file
    
    Outputs: 
    dir_eop  -> [str] Directory for storing EOP file
    """
    if dir_to is None:
        home = str(Path.home())
        dir_to = home + '/src/eop-data/'
    
    file = 'finals2000A.all'
    dir_file = dir_to + file
    
    server = 'ftp.iers.org'
    ftp = FTP(server,timeout=200) 
    ftp.login()  
    ftp.cwd('~/products/eop/rapid/standard/') 

    if not path.exists(dir_to): makedirs(dir_to)
    if not path.exists(dir_file):
        desc = "Downloading the latest EOP file '{:s}' from IERS".format(file)
        tqdm_ftp(ftp,dir_to,file,desc)
    else:
        modified_time = datetime.fromtimestamp(path.getmtime(dir_file))
        if datetime.now() > modified_time + timedelta(days=out_days):
            remove(dir_file)
            desc = "Updating the EOP file '{:s}' from IERS".format(file)
            tqdm_ftp(ftp,dir_to,file,desc)
        else:
            print("The EOP file '{0:s}' in {1:s} is already the latest.".format(file,dir_to)) 

    return dir_to        

def download_ephem(eph,dir_to=None):
    """
    Download JPL ephemeris files from NAIF.

    Usage: 
    >>> eph = 'de430' # or 'de440'
    >>> dir_ephem = download_ephem(eph)

    Parameters: 
    dir_ephem  -> [str, optional, default = None] Directory for storing EOP file.

    Inputs: 
    eph        -> [str] Version of the JPL ephemeris, such as 'de430'
    
    Outputs: 
    dir_ephem  -> [str] Directory for storing the JPL ephemeris file
    """
    if dir_to is None:
        home = str(Path.home())
        dir_to = home + '/src/ephem-data/'

    file = eph + '.bsp'    
    dir_file = dir_to + file
    url = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/' + file

    if not path.exists(dir_to): makedirs(dir_to)
    if not path.exists(dir_file):
        desc = "Downloading the JPL ephemeris file '{:s}' from NAIF".format(eph)
        tqdm_request(url,dir_to,file,desc)
    else:
    	print("The JPL ephemeris file '{:s}' is already in {:s}.".format(file,dir_to)) 

    return dir_to 

def tle_download(noradids):
    '''
    Download the TLE/3LE data from https://www.space-track.org

    Usage: 
    tlefile = tle_download(noradids)
    tlefile = tle_download('satno.txt')

    Inputs:
    noradids -> [str, int, list of str/int] NORADID of space targets. 
    It can be a single NORADID, list of NORADID, or a file containing a set of NORADID.
    The form and format of the file is as follows:
    #satno
    12345
    23469
    ...

    Outputs: 
    tlefile  -> [str] Path of TLE/3LE file.
    '''
    # Check whether a list is empty or not
    if not noradids: raise Exception('noradids is empty.')

    if type(noradids) is int:
        noradids = str(noradids)  
    elif type(noradids) is list:
        if type(noradids[0]) is int: noradids = [str(i) for i in noradids]    
    elif '.' in noradids: # noradids as a file
        noradids = list(set(np.loadtxt(noradids,dtype=np.str)))
    else:
        pass        
    
    # username and password for Space-Track
    home = str(Path.home())
    direc = home + '/src/spacetrack-data/'
    loginfile = direc + 'spacetrack-login'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(loginfile):
        username = input('Please input the username for Space-Track(which can be created at https://www.space-track.org/auth/login): ')
        password = input('Please input the password for Space-Track: ')
        outfile = open(loginfile,'w')
        for element in [username,password]:
            outfile.write('{:s}\n'.format(element))
        outfile.close()
    else:
        infile = open(loginfile,'r')
        username = infile.readline().strip()
        password = infile.readline().strip()
        infile.close()

    st = SpaceTrackClient(username, password)
    lines_tle = st.tle_latest(norad_cat_id=noradids,ordinal=1,iter_lines=True,format='tle')
    
    # save TLE/3LE data to files
    dir_TLE = 'TLE/'   
    fileList_TLE = glob(dir_TLE+'*')
    if path.exists(dir_TLE):
        for file in fileList_TLE:
            remove(file)
    else:
        mkdir(dir_TLE) 
        
    valid_ids = []
    file_tle = open(dir_TLE+'satcat_tle.txt','w')
    print('Downloading TLE data',end=' ... ')
    for line in lines_tle:
        words = line.split()
        if words[0] == '2': valid_ids.append(words[1])
        file_tle.write(line+'\n')
    file_tle.close()  
    print('Complete')
    if type(noradids) is not list: noradids = [noradids]
    missing_ids = list(set(noradids)-set(valid_ids))
    if missing_ids: print('Note: TLE data for these targets are not avaliable: ',missing_ids) 

    return dir_TLE+'satcat_tle.txt'          