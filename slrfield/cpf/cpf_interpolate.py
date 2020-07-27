import numpy as np
from astropy import units as u
from astropy.time import Time,TimeDelta
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from scipy.interpolate import BarycentricInterpolator
from scipy.constants import speed_of_light

def cpf_interpolate(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment,mode,station,coord_type):
    '''
    Interpolate the CPF ephemeris and make the prediction

    Usage: 
    ts_iso,ts_mjd,ts_sod,az,alt,r,tof1 = cpf_interpolate(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment,mode,station,coord_type)
    ts_iso,ts_mjd,ts_sod,az_trans,alt_trans,delta_az,delta_alt,r_trans,tof2 = cpf_interpolate(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment,mode,station,coord_type)


    Inputs:
    ts_utc_cpf -> [str array] iso-formatted UTC for CPF ephemeris 
    ts_mjd_cpf -> [int array] MJD for CPF ephemeris 
    ts_sod_cpf -> [float array] Second of Day for CPF ephemeris 
    leap_second_cpf -> [int array] Leap second for CPF ephemeris 
    positions_cpf -> [2d float array] target positions in cartesian coords in meters w.r.t. ITRF for CPF ephemeris 
    t_start -> [str] starting date and time of ephemeris 
    t_end -> [str] ending date and time of ephemeris
    t_increment -> [float or int] time increment in second for ephemeris interpolation, such as 0.5, 1, 2, 5, etc. 
    mode -> [str] whether to consider the light time; if 'geometric', instantaneous position vector from station to target is computed; 
    if 'apparent', position vector containing light time from station to target is computed.
    station -> [numercial array or list with 3 elements] coordinates of station. It can either be geocentric(x, y, z) coordinates or geodetic(lon, lat, height) coordinates.
    Unit for (x, y, z) are meter, and for (lon, lat, height) are degree and meter.
    coord_type -> [str] coordinates type for coordinates of station; it can either be 'geocentric' or 'geodetic'.

    Outputs:
    (1) If the mode is 'geometric', then the transmitting direction of the laser coincides with the receiving direction at a certain moment. 
    In this case, the light time is not considered and the outputs are
    ts_iso -> [str array] iso-formatted UTC for interpolated prediction
    ts_mjd -> [int array] MJD for interpolated prediction
    ts_sod -> [float array] Second of Day for for interpolated prediction
    az -> [float array] Azimuth for interpolated prediction in degrees
    alt -> [float array] Altitude for interpolated prediction in degrees
    r -> [float array] Range for interpolated prediction in meters
    tof1 -> [float array] Time of flight for interpolated prediction in seconds

    (2) If the mode is 'apparent', then the transmitting direction of the laser is inconsistent with the receiving direction at a certain moment. 
    ts_iso -> [str array] iso-formatted UTC for interpolated prediction
    In this case, the light time is considered and the outputs are
    ts_mjd -> [int array] MJD for interpolated prediction
    ts_sod -> [float array] Second of Day for for interpolated prediction
    az_trans -> [float array] Transmitting azimuth for interpolated prediction in degrees
    alt_trans -> [float array] Transmitting altitude for interpolated prediction in degrees
    delta_az -> [float array] The difference of azimuth between the receiving direction and the transmitting direction in degrees
    delta_alt -> [float array] The difference of altitude between the receiving direction and the transmitting direction in degrees
    r_trans -> [float array] Transmitting range for interpolated prediction in meters
    tof2 -> [float array] Time of flight for interpolated prediction in seconds
    '''
    t_start,t_end = Time(t_start),Time(t_end)
    t_start_interp,t_end_interp = Time(ts_utc_cpf[4]),Time(ts_utc_cpf[-5])
    
    if t_start < t_start_interp or t_end > t_end_interp:
        raise ValueError('({:s}, {:s}) is outside the interpolation range of prediction ({:s}, {:s})'.format(t_start.iso, t_end.iso,t_start_interp.iso,t_end_interp.iso))
        
    dt = np.around((t_end - t_start).to(u.second).value)
    ts = t_start + TimeDelta(np.arange(0,dt,t_increment), format='sec')    
    ts_mjd = ts.mjd.astype(int) 
    ts_iso = ts.iso
    ts_sod = iso2sod(ts_iso)

    leap_second = np.zeros_like(ts_mjd)

    ts_mjd_median = np.median(ts_mjd_cpf)
    ts_mjd_demedian = ts_mjd - ts_mjd_median
    ts_mjd_cpf_demedian = ts_mjd_cpf - ts_mjd_median

    if leap_second_cpf.any(): # Identify whether the CPF ephemeris includes the leap second
        leap_second_boundary = np.diff(leap_second_cpf).nonzero()[0][0] + 1 
        value = leap_second_cpf[leap_second_boundary]
        mjd_cpf_boundary = ts_mjd_cpf[leap_second_boundary]

        condition = (ts_mjd == mjd_cpf_boundary) # 
        
        # If the CPF ephemeris includes the leap second, then we need to identify whether the interpolated prediction includes the leap second.
        if condition.any(): 
            leap_index = np.where(condition)[0][0]
            leap_second[leap_index:] = value

    ts_quasi_mjd = ts_mjd_demedian + (ts_sod+leap_second)/86400
    ts_quasi_mjd_cpf = ts_mjd_cpf_demedian + (ts_sod_cpf+leap_second_cpf)/86400

    positions = interp_ephem(ts_quasi_mjd,ts_quasi_mjd_cpf,positions_cpf)
    az,alt,r = itrs2horizon(station,ts,ts_quasi_mjd,positions,coord_type)

    if mode == 'geometric':   
        tof1 = 2*r/speed_of_light
        return ts_iso,ts_mjd,ts_sod,az,alt,r,tof1

    elif mode == 'apparent':

        tau = r/speed_of_light
        ts_quasi_mjd_trans = ts_mjd_demedian + (ts_sod+leap_second+tau)/86400
        ts_quasi_mjd_recei = ts_mjd_demedian + (ts_sod+leap_second-tau)/86400
        positions_trans = interp_ephem(ts_quasi_mjd_trans,ts_quasi_mjd_cpf,positions_cpf)
        positions_recei = interp_ephem(ts_quasi_mjd_recei,ts_quasi_mjd_cpf,positions_cpf)
        az_trans,alt_trans,r_trans = itrs2horizon(station,ts,ts_quasi_mjd_trans,positions_trans,coord_type)
        az_recei,alt_recei,r_recei = itrs2horizon(station,ts,ts_quasi_mjd_recei,positions_recei,coord_type)
        tof2 = 2*r_trans/speed_of_light
        delta_az = az_recei - az_trans
        delta_alt = alt_recei - alt_trans

        return ts_iso,ts_mjd,ts_sod,az_trans,alt_trans,delta_az,delta_alt,r_trans,tof2
    else:
        raise Exception("Mode must be 'geometric' or 'apparent'.")      

def interp_ephem(ts_quasi_mjd,ts_quasi_mjd_cpf,positions_cpf):
    '''
    Interpolate the CPF ephemeris using the 10-point(degree 9) Lagrange polynomial interpolation method. 

    Usage: 
    positions = interp_ephem(ts_quasi_mjd,ts_quasi_mjd_cpf,positions_cpf)

    Inputs:
    Here, the quasi MJD is defined as int(MJD) + (SoD + Leap Second)/86400, which is different from the conventional MJD defination.
    For example, MJD and SoD for '2016-12-31 23:59:60' are 57753.99998842606 and 86400, but the corresponding quasi MJD is 57754.0 with leap second of 0.
    As a comparison, MJD and SoD for '2017-01-01 00:00:00' are 57754.0 and 0, but the corresponding quasi MJD is 57754.00001157408 with leap second of 1.
    The day of '2016-12-31' has 86401 seconds, and for conventional MJD calculation, one second is compressed to a 86400/86401 second. 
    Hence, the quasi MJD is defined for convenience of interpolation.

    ts_quasi_mjd -> [float array] quasi MJD for interpolated prediction
    ts_quasi_mjd_cpf -> [float array] quasi MJD for CPF ephemeris
    positions_cpf -> [2d float array] target positions in cartesian coordinates in meters w.r.t. ITRF for CPF ephemeris. 

    Outputs:
    positions -> [2d float array] target positions in cartesian coordinates in meters w.r.t. ITRF for interpolated prediction.
    '''
    positions = []

    m = len(ts_quasi_mjd)
    n = len(ts_quasi_mjd_cpf)

    if m > n:
        for i in range(n-1):
            flags = (ts_quasi_mjd >= ts_quasi_mjd_cpf[i]) & (ts_quasi_mjd < ts_quasi_mjd_cpf[i+1])
            if flags.any(): 
                positions.append(BarycentricInterpolator(ts_quasi_mjd_cpf[i-4:i+6],positions_cpf[i-4:i+6])(ts_quasi_mjd[flags]))
        positions = np.concatenate(positions)        
    else:
        for j in range(m):
            boundary = np.diff(ts_quasi_mjd[j] >= ts_quasi_mjd_cpf).nonzero()[0][0]
            if ts_quasi_mjd[j] in  ts_quasi_mjd_cpf:
                positions.append(positions_cpf[boundary])
            else:    
                positions.append(BarycentricInterpolator(ts_quasi_mjd_cpf[boundary-4:boundary+6],positions_cpf[boundary-4:boundary+6])(ts_quasi_mjd[j]))
        positions = np.array(positions)   

    return positions    

def itrs2horizon(station,ts,ts_quasi_mjd,positions,coord_type):
    '''
    Convert cartesian coordinates of targets in ITRF to spherical coordinates in topocentric reference frame for a specific station.

    Usage: 
    az,alt,r = itrs2horizon(station,ts,ts_quasi_mjd,positions,coord_type)

    Inputs:
    station -> [numercial array or list with 3 elements] coordinates of station. It can either be geocentric(x, y, z) coordinates or geodetic(lon, lat, height) coordinates.
    Unit for (x, y, z) are meter, and for (lon, lat, height) are degree and meter.
    ts -> [str array] iso-formatted UTC for interpolated prediction
    ts_quasi_mjd -> [float array] quasi MJD for interpolated prediction
    positions -> [2d float array] target positions in cartesian coordinates in meters w.r.t. ITRF for interpolated prediction.
    coord_type -> [str] coordinates type for coordinates of station; it can either be 'geocentric' or 'geodetic'.

    Outputs:
    az -> [float array] Azimuth for interpolated prediction in degrees
    alt -> [float array] Altitude for interpolated prediction in degrees
    r -> [float array] Range for interpolated prediction in meters
    '''
    if coord_type == 'geocentric':
        x,y,z = station
        site = EarthLocation.from_geocentric(x, y, z, unit='m')
    elif coord_type == 'geodetic':
        lat,lon,height = station
        site = EarthLocation.from_geodetic(lon, lat, height)

    coords = SkyCoord(positions,unit='m',representation_type = 'cartesian',frame = 'itrs',obstime = Time(ts))
    horizon = coords.transform_to(AltAz(obstime = Time(ts),location = site))

    az,alt,r = horizon.az.deg, horizon.alt.deg, horizon.distance.m

    return az,alt,r

def iso2sod(ts):
    '''
    Calculate the Second of Day from the iso-formatted UTC time sets.

    Usage: 
    sods = iso2sod(ts)

    Inputs:
    ts -> [str array] iso-formatted UTC time sets

    Outputs:
    sods -> [float array] second of day
    '''
    sods = []
    for t in ts:
        sod = int(t[11:13])*3600 + int(t[14:16])*60 + float(t[17:])
        sods.append(sod)
    return np.array(sods)
