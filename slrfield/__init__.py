'''
slrfield package

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging).   
Currently, operations on SLR data include:
    1. Automatically download the CPF(Consolidated Prediction Format) ephemeris file
    2. Parse the CPF ephemeris file
    3. Predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of the station
'''

from .cpf_utils.cpf_download import cpf_download
from .cpf_utils.cpf_read import read_cpfs
