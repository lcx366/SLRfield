from astropy.utils import iers as iers_astropy
from .data_download import download_eop

def time_load():

    # load the EOP file
    eop_file = download_eop()

    # for astropy
    iers_a = iers_astropy.IERS_A.open(eop_file)
    eop_table = iers_astropy.earth_orientation_table.set(iers_a)