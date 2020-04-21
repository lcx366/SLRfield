# Welcome to the SLRfield package

This package is an archive of scientific routines for data processing related to SLR(Satellite Laser Ranging). 
Currently, operations on SLR data include:

1. Automatically download the CPF(Consolidated Prediction Format) ephemeris file

2. Parse the CPF ephemeris file

3. Predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of a station 

## How to Install

SLRfield can be installed with `pip install slrfield`.

## How to Upgrade

SLRfield can be updated to the latest version with `pip install slrfield --upgrade`.

## How to use

### Download the latest CPF ephemeris files at the current moment

In this package, for prediction data centers, only **CDDIS**(Crustal Dynamics Data Information System) and **EDC**(EUROLAS Data Center) are available. If the prediction data center is not provided, then it is set to **CDDIS** by default.

#### Download all available targets

```python
>>> from slrfield import cpf_download
>>> cpf_files_all = cpf_download()
Downloading ...  swarmb_cpf_200420_6111.esa ... 226 Transfer complete.
Downloading ...  swarma_cpf_200420_6111.esa ... 226 Transfer complete.
...
Downloading ...  compassi5_cpf_200412_6031.sha ... 226 Transfer complete.
Downloading ...  compassi3_cpf_200412_6031.sha ... 226 Transfer complete.
>>> print(cpf_files_all)
['CPF/CDDIS/2020-04-20/swarmb_cpf_200420_6111.esa',
 'CPF/CDDIS/2020-04-20/swarma_cpf_200420_6111.esa',
 ...,
 'CPF/CDDIS/2020-04-20/compassi5_cpf_200412_6031.sha',
 'CPF/CDDIS/2020-04-20/compassi3_cpf_200412_6031.sha']
# From EDC
# cpf_files_all = cpf_download(source = 'EDC')
```
#### Download a set of specified targets

From ***CDDIS*** by default

```python
>>> sat_lists = ['ajisai','lageos1','hy2a','etalon2','jason3']
>>> cpf_files_cddis = cpf_download(sat_lists) 
Downloading ...  etalon2_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  lageos1_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  ajisai_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  jason3_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  hy2a_cpf_200420_6111.sha ... 226 Transfer complete.
```

From ***EDC***

```python
>>> sat_lists = ['ajisai','lageos1','hy2a','etalon2','jason3']
>>> cpf_files_edc = cpf_download(sat_lists,source = 'EDC') 
Downloading ...  ajisai_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  etalon2_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  jason3_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  lageos1_cpf_200420_6111.hts ... 226 Transfer complete.
Downloading ...  hy2a_cpf_200420_6111.sha ... 226 Transfer complete.
```

### Download the latest CPF ephemeris files before a specific date and time

From ***CDDIS*** by default

```python
>>> sat_name = 'lageos1'
>>> date = '2007-06-01 11:30:00'
>>> cpf_file_cddis = cpf_download(sat_name,date)
Downloading ...  lageos1_cpf_070601_6521.sgf ... 226 Transfer complete.
>>> print(cpf_file_cddis)
['CPF/CDDIS/2007-06-01/lageos1_cpf_070601_6521.sgf']
```

From ***EDC***

```python
>>> sat_lists = ['starlette','lageos1']
>>> date = '2017-01-01 11:30:00'
>>> cpf_files_edc = cpf_download(sat_lists,date,'EDC')
Downloading ...  starlette_cpf_170101_8662.hts ... 226 Transfer complete.
Downloading ...  lageos1_cpf_170101_8662.hts ... 226 Transfer complete.
>>> print(cpf_files_edc)
['CPF/EDC/2017-01-01/starlette_cpf_170101_8662.hts', 'CPF/EDC/2017-01-01/lageos1_cpf_170101_8662.hts']
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

## Change log

- **0.0.1 — Apr 21,  2020**
- The ***slrfield*** package was released.
  

## Next release

 - Complete the help documentation

 - Improve the code structure to make it easier to read

 - Add functions to download, parse, and handle the CRD(**Consolidated Laser Ranging Data Format**) observations

## Reference

- [Python package for satellite laser ranging file formats](https://github.com/dronir/SLRdata)
- [Consolidated Laser Ranging Prediction Format Version 1.01](https://ilrs.gsfc.nasa.gov/docs/2006/cpf_1.01.pdf)
- [sample code](https://ilrs.gsfc.nasa.gov/docs/2017/cpf_sample_code_v1.01d.tgz) on [ILRS](https://ilrs.gsfc.nasa.gov/data_and_products/formats/cpf.html)
