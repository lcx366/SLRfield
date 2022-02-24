
from datetime import datetime,timedelta
from os import path,makedirs,remove
from pathlib import Path
from ftplib import FTP

from .try_download import tqdm_ftp

def download_eop(out_days=7,dir_to=None):
    """
    Download or update the Earth Orientation Parameters(EOP) file from IERS

    Usage: 
        >>> eop_file = download_eop()

    Parameters: 
        out_days -> [int, default = 7] Update cycle of the EOP file
        dir_to   -> [str, default = None] Directory for storing EOP file
    
    Outputs: 
        eop_file -> [str] Path of the EOP file
    """
    if dir_to is None:
        home = str(Path.home())
        dir_to = home + '/src/eop-data/'
    
    file = 'finals2000A.all'
    dir_file = dir_to + file

    server = 'ftp.iers.org'
    src_dir = '~/products/eop/rapid/standard/'

    if not path.exists(dir_to): makedirs(dir_to)
    if not path.exists(dir_file):
        ftp_access(server,src_dir)
        desc = "Downloading the latest EOP '{:s}' from IERS".format(file)
        tqdm_ftp(ftp,dir_to,file,desc)
    else:
        modified_time = datetime.fromtimestamp(path.getmtime(dir_file))
        if datetime.now() > modified_time + timedelta(days=out_days):
            remove(dir_file)
            ftp_access(server,src_dir)
            desc = "Updating EOP '{:s}' from IERS".format(file)
            tqdm_ftp(ftp,dir_to,file,desc)
        else:
            print("EOP '{0:s}' in {1:s} is already the latest.".format(file,dir_to)) 

    return dir_file  