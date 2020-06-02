import numpy as np
import os,glob
from pathlib import Path
from spacetrack import SpaceTrackClient

def tle_download(noradids):
    '''
    Download the TLE/3LE data from https://www.space-track.org

    Usage: 
    tlefile = tle_download(noradids)
    tlefile = tle_download('satno.txt')

    Inputs:
    noradids -> [str, int, list of str, or list of int] NORADID; it can be a single NORADID, list of NORADID, or a file containing a set of NORADID.
    The form and format of the file is as follows:
    #satno
    12345
    23469
    ...

    Outputs: 
    tlefile -> [str] Path of TLE/3LE file
    '''
    # noradids as a file
    if '.' in noradids:
        noradids = list(set(np.loadtxt(noradids,dtype=np.str)))
    elif type(noradids) is int:
        noradids = str(noradids)
    elif type(noradids) is list:
        if type(noradids[0]) is int: noradids = [str(i) for i in noradids]    
    else:
        pass        
    
    # username and password for Space-Track
    home = str(Path.home())
    direc = home + '/src/spacetrack-data/'
    loginfile = direc + 'spacetrack-login'

    if not os.path.exists(direc): makedirs(direc)
    if not os.path.exists(loginfile):
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
    lines_3le = st.tle_latest(norad_cat_id=noradids,ordinal=1,iter_lines=True,format='3le')
    
    # save TLE/3LE data to files
    dir_TLE = 'TLE/'   
    fileList_TLE = glob.glob(dir_TLE+'*')
    if os.path.exists(dir_TLE):
        for file in fileList_TLE:
            os.remove(file)
    else:
        os.mkdir(dir_TLE) 
        
    valid_ids = []
    file_3le = open(dir_TLE+'satcat_3le.txt','w')
    for line in lines_3le:
        words = line.split()
        if words[0] == '2': valid_ids.append(words[1])
        file_3le.write(line+'\n')
    file_3le.close()  
    missing_ids = list(set(noradids)-set(valid_ids))
    if missing_ids: print('TLE data for these targets are not avaliable: ',missing_ids) 
    print('Complete the download of TLE data.\n ')

    return dir_TLE+'satcat_3le.txt'       