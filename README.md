# Welcome to the SLRfield package

[![PyPI version shields.io](https://img.shields.io/pypi/v/slrfield.svg)](https://pypi.python.org/pypi/slrfield/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/slrfield.svg)](https://pypi.python.org/pypi/slrfield/) [![PyPI status](https://img.shields.io/pypi/status/slrfield.svg)](https://pypi.python.org/pypi/slrfield/) [![GitHub contributors](https://img.shields.io/github/contributors/lcx366/SLRfield.svg)](https://GitHub.com/lcx366/SLRfield/graphs/contributors/) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/lcx366/SLRfield/graphs/commit-activity) [![GitHub license](https://img.shields.io/github/license/lcx366/SLRfield.svg)](https://github.com/lcx366/SLRfield/blob/master/LICENSE) [![Documentation Status](https://readthedocs.org/projects/pystmos/badge/?version=latest)](http://slrfield.readthedocs.io/?badge=latest) [![Build Status](https://travis-ci.org/lcx366/SLRfield.svg?branch=master)](https://travis-ci.org/lcx366/SLRfield)

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging). 
Currently, operations on SLR data include:

1. Download CPF(Consolidated Prediction Format) ephemeris files automatically from **CDDIS**(Crustal Dynamics Data Information System) or **EDC**(EUROLAS Data Center);
2. Parse the CPF ephemeris files;
3. Given the position of a site, predict the azimuth, altitude, distance of targets, and the time of flight for laser pulse etc.;
4. Download the TLE/3LE data from [SPACETRACK](https://www.space-track.org) automatically;
5. Pick out targets from [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) and [CELESTRAK](https://celestrak.com) database by setting a series of parameters, such as mass, shape, RCS(Radar Cross Section), and orbit altitude etc.;
6. Calculate one-day prediction and multiple-day visible passes for space targets based on the TLE/3LE data;

## How to Install

On Linux, macOS and Windows architectures, the binary wheels can be installed using pip by executing one of the following commands:

```
pip install slrfield
pip install slrfield --upgrade # to upgrade a pre-existing installation
```

## How to use

### Download the latest CPF ephemeris files at the current moment

If the prediction release center is not provided, the CPF ephemeris files are downloaded from **CDDIS** by default.

#### Download all available targets

A data storage directory, such as CPF/CDDIS/2020-10-02, will be automatically created.  If it already exists, it will be ***emptied*** by default once the download starts. By setting `append = True`, the data storage directory will  ***not*** be ***emptied***.

```python
>>> from slrfield import cpf_download
>>> cpf_files_all = cpf_download() # From CDDIS by default
>>> # cpf_files_all = cpf_download(source = 'EDC') # From EDC
```

```python
>>> cpf_files_append = cpf_download(['beaconc','lageos1'],append=True)
```

#### Download a set of specified targets

```python
>>> sat_lists = ['ajisai','lageos1','etalon2','jason3']
>>> cpf_files_cddis = cpf_download(sat_lists) # From CDDIS
>>> cpf_files_edc = cpf_download(sat_lists,source = 'EDC') # From EDC
```

### Download the latest CPF ephemeris files before a specific date and time

```python
>>> sat_name = 'lageos1'
>>> date = '2007-06-01 11:30:00'
>>> cpf_file_cddis = cpf_download(sat_name,date) # From CDDIS
>>> sat_lists = ['starlette','lageos1']
>>> date = '2017-01-01 11:30:00'
>>> cpf_files_edc = cpf_download(sat_lists,date,'EDC') # From EDC
```

### Parse the CPF ephemeris files and read the data

Information from the parsed CPF ephemeris files includes the following contents:
 - Format
 - Format Version
 - Ephemeris Source
 - Date and time of ephemeris production
 - Ephemeris Sequence number
 - Target name
 - COSPAR ID
 - SIC
 - NORAD ID
 - Starting date and time of ephemeris
 - Ending date and time of ephemeris
 - Time between table entries (UTC seconds)
 - Target type
 - Reference frame
 - Rotational angle type
 - Center of mass correction
 - Direction type
 - Modified Julian Date
 - Second of Day 
 - Leap Second
 - Time moment in UTC 
 - Target positions in meters

#### Parse a single CPF ephemeris file

```python
>>> from slrfield import read_cpfs
>>> cpf_data_cddis = read_cpfs(cpf_file_cddis)
>>> print(cpf_data_cddis.info)
[{'MJD': array([54252, 54252, ..., 54254, 54254]),'SoD': array([0., 300., ..., 85800., 86100.]),'positions[m]': array([[ 6033709.581,  6786287.416, 8199639.624], ..., [ 3434366.77 , -2533996.246, 11511370.917]]),'Leap_Second': array([0, 0, ..., 0, 0]),'Format': 'CPF', 'Format Version': '1', 'Ephemeris Source': 'SGF', 'Time of Ephemeris Production': '2007-06-01 02:00:00.000', 'Ephemeris Sequence Number': '6521', 'Target Name': 'Lageos1', 'COSPAR ID': '7603901', 'SIC': '1155', 'NORAD ID': '08820', 'Start': '2007-06-01 00:00:00.000', 'End': '2007-06-03 23:54:00.000', 'Time Interval[sec]': '300', 'Target Type': 'passive(retro-reflector) artificial satellite', 'Reference Frame': 'ITRF(default)', 'Rotational Angle': 'Not Applicable', 'Center of Mass Correction': 'None applied. Prediction is for center of mass of target', 'Direction': 'instantaneous vector from geocenter to target, without light-time iteration', 'ts_utc': array(['2007-06-01 00:00:00.000', '2007-06-01 00:05:00.000', ..., '2007-06-03 23:50:00.000', '2007-06-03 23:55:00.000'], dtype='<U23')}]   
```

#### Parse a set of CPF ephemeris files

```python
>>> cpf_data_edc = read_cpfs(cpf_files_edc)
>>> print(cpf_data_edc.target_name)
['starlette', 'lageos1']
>>> print(cpf_data_edc.ephemeris_source)
['HTS', 'HTS']
>>> print(cpf_data_edc.norad_id)
['7646', '8820']
>>> print(cpf_data_edc.cospar_id)
['7501001', '7603901']
>>> print(cpf_data_edc.time_ephemeris) # Date and time of ephemeris production
['2016-12-31 12:00:00.000', '2016-12-31 12:00:00.000']
>>> print(cpf_data_edc.version) # Format Version
['1', '1']
```

### Make predictions

The azimuth, altitude, distance of a target w.r.t. a given station, and the time of flight for laser pulse etc. can be easily predicted by calling a method `pred`. The output prediction files named with target names are stored in directory pred by default. 

- There are two modes for the prediction. If the mode is set to ***geometric***, then the transmitting direction of the laser will coincide with the receiving direction at a certain moment. In this case, the output prediction file will not contain the difference between the receiving direction and the transmitting direction. If the mode is set to ***apparent***, then the transmitting direction of the laser is inconsistent with the receiving direction at a certain moment. In this case, the output prediction file will contain the difference between the receiving direction and the transmitting direction. The default mode is set to ***apparent***.
- The 10-point(degree 9) Lagrange polynomial interpolation method is used to interpolate the CPF ephemeris.
- Effects of leap second have been considered in the prediction generation.

Coordinates of station can either be ***geocentric***(x, y, z) in meters or ***geodetic***(lon, lat, height) in degrees and meters. The default coordinates type is set to ***geodetic***.

Note: The first use of slrfield will call [astropy](https://www.astropy.org) to automatically download the **Earth Orientation Parameters** file, so it may take a long time to output the prediction file.

#### For geodetic(lon, lat, height) station coordinates

```python
t_start = '2007-06-01 17:06:40'
t_end = '2007-06-02 09:06:40'
t_increment = 0.5 # second

station = [46.877230,7.465222,951.33] # geodetic(lon, lat, height) coordinates in degrees and meters by default
cpf_data_cddis.pred(station,t_start,t_end,t_increment)
```

####  For geocentric(x, y, z) station coordinates

```python
t_start = '2017-01-01 22:06:40'
t_end = '2017-01-02 09:06:40'
t_increment = 2 # second

station = [4331283.557, 567549.902,4633140.353] # geocentric(x, y, z) coordinates in meters
cpf_data_edc.pred(station,t_start,t_end,t_increment,coord_type = 'geocentric',mode='geometric')
```

### Pick out space targets

Pick out space targets that meets specific physical characteristics from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database. The DISCOS database mainly provides the geometric information of the spatial target, such as shape, size and mass, etc. Before using this package to access the DISCOS database, you need to register an account and get a token. 

```python
from slrfield import discos_query
result = discos_query(Shape=['Box','Pan','+'],Length=[0.5,5],Mass=[300,500],sort='Mass')
```

 A pandas dataframe and a csv-formatted file *discos_catalog.csv* will be returned. 

Pick out space targets that meets specific orbital demands from the  [CELESTRAK](https://celestrak.com) database. The CELESTRAK database mainly provides information such as the orbit inclination, period, and altitude, etc. 

``` python
from slrfield import celestrak_query
result = celestrak_query(Payload=False,Decayed=False,MeanAlt=None=[400,1000],sort='-Inclination')
```

A pandas dataframe and a csv-formatted file *celestrak_catalog.csv* will be returned. 

Pick out space targets from the combination of DISCOS and CELESTRAK.

```python
from slrfield import target_query
targets_df = target_query(Payload=False,Decayed=False,RCSAvg=[5,100],MeanAlt=[300,800])
# The file 'noradids.txt' records the target's NORAD ids
# targets_df = target_query(NORADID = 'noradids.txt')
```

A pandas dataframe and a csv-formatted file *target_catalog.csv* will be returned. 

### Download TLE/3LE data

Download the TLE/3LE data from [SPACE-TRACK](https://www.space-track.org); before using this package to access the TLE/3LE database, you need to register an account. 

```python
from slrfield import tle_download
noradids = list(targets_df['NORADID'])
# noradids = 'satno.txt'
satcat_tle = tle_download(noradids)
```

A  text file *satcat_tle.txt* will be created in the directory TLE.

### Calculate the visible passes for target transit

```python
from slrfield import visible_pass
t_start = '2020-06-08 23:00:00' # starting date and time 
t_end = '2020-06-11 00:00:00' # ending date and time
timezone = 8 # timezone
site = ['25.03 N','102.80 E','1987.05'] # station position in lat[deg], lon[deg], and height[m] above the WGS84 ellipsoid
visible_pass(t_start,t_end,site,timezone)
```

csv-formatted file *VisiblePasses_bysat.csv* and *VisiblePasses_bydate.csv*, as well as a set of text file xxxx.txt will be created in the directory prediction, where 'xxxx' represents the NORADID of the target.

## Change log

- **0.1.14 — Jun 18,  2021**

  Fixed the problem that EOP could not be downloaded normally from IERS.

- **0.1.13 — Jun 05,  2021**

  Now you may inject the NORAD IDs of a large number of targets by an input file such as *noradids.txt* to  `target_query`.

- **0.1.11 — Oct 03,  2020**

  The CDDIS will discontinue anonymous ftp access to its archive in October 2020, therefore, this package implements the transition from ftp to EARTHDATA for downloading CPF files.

- **0.1.9 — Jul 26,  2020**

  Added progress bar for downloading data

- **0.1.5 — Jun 9,  2020**

  Expanded the following functions：

  - Automatically download TLE/3LE data from [SPACETRACK](https://www.space-track.org)
  - Pick out space targets that meets specific demands from [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) and [CELESTRAK](https://celestrak.com) database by setting a series of parameters, such as mass, shape, RCS(Radar Cross Section), and orbit altitude etc.
  - Calculate one-day prediction and multiple-day visible passes for space targets based on TLE/3LE data

- **0.0.2 — Apr 21,  2020**
  
  - The ***slrfield*** package was released.

## Next release

 - Improve the code structure to make it easier to read
 - Add functions to download, parse, and handle the CRD(**Consolidated Laser Ranging Data Format**) observations
 - Add  functions to estimate the apparent magnitude of the target

## Reference

- [Python package for satellite laser ranging file formats](https://github.com/dronir/SLRdata)
- [Consolidated Laser Ranging Prediction Format Version 1.01](https://ilrs.gsfc.nasa.gov/docs/2006/cpf_1.01.pdf)
- [sample code](https://ilrs.gsfc.nasa.gov/docs/2017/cpf_sample_code_v1.01d.tgz) on [ILRS](https://ilrs.gsfc.nasa.gov/data_and_products/formats/cpf.html)
- [Skyfield-Elegant Astronomy for Python](https://rhodesmill.org/skyfield/)
- [DISCOS](https://discosweb.esoc.esa.int)
- [CELESTRAK](https://celestrak.com) 
- [SPACE-TRACK](https://www.space-track.org)
