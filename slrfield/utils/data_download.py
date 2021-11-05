
import numpy as np
from os import path,mkdir,makedirs,remove
from glob import glob
from pathlib import Path
from ftplib import FTP
from datetime import datetime,timedelta
from spacetrack import SpaceTrackClient
from time import sleep
from colorama import Fore

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

def tle_download(noradids,mode='keep'):
    '''
    Download the TLE/3LE data from https://www.space-track.org

    Usage: 
        tlefile = tle_download(noradids)
        tlefile = tle_download(noradids,'clear')
        tlefile = tle_download('satno.txt')

    Inputs:
        noradids -> [str, int, list of str/int] NORADID of space targets. 
        It can be a single NORADID, list of NORADID, or a file containing a set of NORADID.
        The form and format of the file is as follows:
        #satno
        12345
        23469
        ...

    Parameters:
        mode -> [str,default='keep'] either keep the files stored in TLE directory or clear the TLE directory 

    Outputs: 
        tlefile  -> [str] Path of TLE/3LE file.
    '''
    # Check whether a list is empty or not
    if not noradids: raise Exception('noradids is empty.')

    if type(noradids) is list:
        if type(noradids[0]) is int: noradids = [str(i) for i in noradids]    
    else:
        noradids = str(noradids)
        if '.' in noradids: # noradids as a file
            noradids = list(set(np.loadtxt(noradids,dtype=str)))
        else:
            noradids = [noradids]    
    
    # Set the maximum of requested URL's length with a single access 
    # The setup prevents exceeding the capacity limit of the server
    n = 500
    noradids_parts = [noradids[i:i + n] for i in range(0, len(noradids), n)]  
    part_num = len(noradids_parts)    
    
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
    
    # save TLE/3LE data to files
    dir_TLE = 'TLE/'   
    fileList_TLE = glob(dir_TLE+'*')
    if path.exists(dir_TLE):
        if mode == 'clear':
            for file in fileList_TLE:
                remove(file)
    else:
        mkdir(dir_TLE) 

    valid_ids,j = [],1
    date_str = datetime.utcnow().strftime("%Y%m%d")
    filename_tle = dir_TLE + 'tle_{:s}.txt'.format(date_str)
    file_tle = open(filename_tle,'w')  

    st = SpaceTrackClient(username, password)
    for part in noradids_parts:
        desc = 'Downloading TLE data: Part {:s}{:2d}{:s} of {:2d}'.format(Fore.BLUE,j,Fore.RESET,part_num)
        print(desc,end='\r')
        lines_tle = st.tle_latest(norad_cat_id=part,ordinal=1,iter_lines=True,format='tle')    
        for line in lines_tle:
            words = line.split()
            if words[0] == '2': valid_ids.append(words[1].lstrip('0'))
            file_tle.write(line+'\n')
        sleep(5) 
        j += 1   
    file_tle.close()

    missed_ids = list(set(noradids)-set(valid_ids))
    if missed_ids: 
        missed_ids_filename = dir_TLE + 'missed_ids.txt'
        desc = '{:s}Note: space targets with unavailable TLE are stored in {:s}.{:s} '.format(Fore.RED,missed_ids_filename,Fore.RESET)
        print(desc) 
        np.savetxt(missed_ids_filename,missed_ids,fmt='%s')

    return filename_tle        