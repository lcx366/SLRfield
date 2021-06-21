from skyfield.api import Loader
from .data_download import download_eop,download_ephem

dir_eop = download_eop()
dir_eph = download_ephem('de440')
    
load_eop = Loader(dir_eop)
load_eph = Loader(dir_eph)

ts = load_eop.timescale()
planets = load_eph('de440.bsp')