
from datetime import datetime,timedelta
from os import path,makedirs,remove
from pathlib import Path
import requests

from .try_download import tqdm_request_http


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
    
    file = 'finals.all.iau2000.txt'
    dir_file = dir_to + file

    url = 'https://datacenter.iers.org/data/latestVersion/finals.all.iau2000.txt'

    if not path.exists(dir_to): makedirs(dir_to)

    if path.exists(dir_file):
        # First check if the file needs updating
        modified_time = datetime.fromtimestamp(path.getmtime(dir_file))
        if datetime.now() > modified_time + timedelta(days=out_days):
            remove(dir_file)
            desc = "Updating EOP '{:s}' from IERS".format(file)
        else:
            print("EOP '{0:s}' in {1:s} is already the latest.".format(file,dir_to)) 
            return dir_file
    else:
        desc = "Downloading the latest EOP '{:s}' from IERS".format(file)
        
    if tqdm_request_http(url,dir_to,file,desc) is None:
        print('SLRfield was unable to import Earth Orientation Parameters (EOP) data. ' \
            + 'It is recommended to try again or to manually download this data (finals.all.iau2000.txt)'\
            + f' and place it in {dir_to}.')
        raise ImportError('Unable to download EOP data')

    return dir_file
