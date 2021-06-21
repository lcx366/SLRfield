"""
slrfield package

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging).   
Currently, operations on SLR data include:

1. Download CPF(Consolidated Prediction Format) ephemeris files automatically from **CDDIS**(Crustal Dynamics Data Information System) or **EDC**(EUROLAS Data Center);
2. Parse the CPF ephemeris files;
3. Given the position of a site, predict the azimuth, altitude, distance of targets, and the time of flight for laser pulse etc.;
4. Download the TLE/3LE data from [SPACETRACK](https://www.space-track.org) automatically;
5. Pick out targets from [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) and [CELESTRAK](https://celestrak.com) database by setting a series of parameters, such as mass, shape, RCS(Radar Cross Section), and orbit altitude etc.;
6. Calculate one-day prediction and multiple-day visible passes for space targets based on the TLE/3LE data;
"""
from astropy.utils import iers

from .cpf.cpf_download import cpf_download
from .cpf.cpf_read import read_cpfs
from .query.query import discos_query,celestrak_query,target_query
from .query.visible_pass import visible_pass
from .utils.data_download import tle_download
from .utils import data_prepare

dir_eop = data_prepare.dir_eop
iers_a = iers.IERS_A.open(dir_eop + 'finals2000A.all')  
eop_table = iers.earth_orientation_table.set(iers_a)
