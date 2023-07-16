"""
slrfield package

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging).   
Currently, operations on SLR data include:

1. Download CPF(Consolidated Prediction Format) ephemeris files automatically from **CDDIS**(Crustal Dynamics Data Information System) or **EDC**(EUROLAS Data Center);
2. Parse the CPF ephemeris files;
3. Calculate the position of targets in GCRF;
4. Predict the azimuth, altitude, distance of targets, and the time of flight for laser pulse etc.;
"""

from .cpf.cpf_download import cpf_download,get_cpf_satlist
from .slrclasses.cpfclass import CPF
from .utils import data_prepare

# Load and update the EOP file and Leap Second file
data_prepare.iers_load() 