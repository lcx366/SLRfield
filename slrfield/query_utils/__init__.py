'''
slrfield query_utils subpackage

This subpackage defines the following functions:

# ============================ query ========================= #

download_bycurrent - Download the latest CPF ephemeris files at the current moment

download_bydate - Download the latest CPF ephemeris files before a specific time

cpf_download - It combines the features of download_bycurrent and download_bydate. 
If the date and time are not given, then the latest cpf ephemeris files at the current time are downloaded; 
otherwise, download the latest cpf ephemeris files before the given date and time.

try_download - Connect to the server and try to download the cpf ephemeris files

# ======================== tle_download ====================== #

read_cpf - Parse a single CPF ephemeris file

read_cpfs - Parse a set of CPF ephemeris files

# ======================== visible_pass ====================== #

cpf_interpolate - Interpolate the CPF ephemeris and make the prediction

interp_ephem - Interpolate the CPF ephemeris

itrs2horizon - Convert cartesian coordinates of targets in ITRF to spherical coordinates in topocentric reference frame for a specific station

iso2sod - Calculate Second of Day from 'iso-formatted' time sets, such as '2017-01-02 03:04:05.678'
'''