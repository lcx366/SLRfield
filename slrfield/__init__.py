'''
slrfield package

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging).   
Currently, operations on SLR data include:
    1. Automatically download the CPF(Consolidated Prediction Format) ephemeris file
    2. Parse the CPF ephemeris file
    3. Predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of the station
    4. Automatically download TLE/3LE data from [SPACETRACK](https://www.space-track.org)
    5. Pick out space targets that meets the demand from [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) and [CELESTRAK](https://celestrak.com) database by setting a series of parameters, such as mass, shape, RCS(Radar Cross Section), and orbit altitude etc.
    6. Calculate one-day prediction and multiple-day visible passes based on TLE/3LE data
'''
from .cpf.cpf_download import cpf_download
from .cpf.cpf_read import read_cpfs
from .query.query import discos_query,celestrak_query,target_query
from .query.tle_download import tle_download
from .query.visible_pass import visible_pass
