from glob import glob
from pathlib import Path
from os import path,mkdir,remove
from urllib.request import urlretrieve

import numpy as np
import pandas as pd

from skyfield.api import Topos,Loader,load
from astropy.time import TimeDelta,Time
from astropy import units as u
from astropy.constants import R_earth,R_sun

def t_list(ts,t_start,t_end,t_step=60):
    '''
    Generate a list of time moments based on start time, end time, and time step.

    Usage: 
    t = t_list(ts,t_start,t_end,t_step)

    Inputs:
    ts -> [object of class Skyfield time scale] Skyfield time system; it constitutes 'deltat.data', 'deltat.preds', and 'Leap_Second.dat'
    t_start -> [object of class Astropy Time] start time, such as Time('2020-06-01 00:00:00')
    t_end -> [object of class Astropy Time] end time, such as Time('2020-06-30 00:00:00') 

    Parameters:
    t_step -> [int, optional, default = 60] time step[seconds] 

    Outputs:
    t -> [list of object of class Skyfield Time] list of time moments
    '''
    dt = np.around((t_end - t_start).to(u.second).value)
    t_astropy = t_start + TimeDelta(np.append(np.arange(0,dt,t_step),dt), format='sec')
    t = ts.from_astropy(t_astropy)
    return t
       
def next_pass(ts,t_start,t_end,sat,site,cutoff = 10):
    '''
    Generate the time period for target transit.

    Usage: 
    passes = next_pass(ts,t_start,t_end,sat,site,cutoff)

    Inputs:
    ts -> [object of class Skyfield time scale] Skyfield time system; it constitutes 'deltat.data', 'deltat.preds', and 'Leap_Second.dat'
    t_start -> [object of class Astropy Time] start time, such as Time('2020-06-01 00:00:00')
    t_end -> [object of class Astropy Time] end time, such as Time('2020-06-30 00:00:00') 
    sat -> [object of class Skyfield satellite] satellite from tle
    site -> [object of class Skyfield Topos] station

    Parameters:
    cutoff -> [float, optional, default=10] Satellite Cutoff Altitude Angle

    Outputs:
    t -> [list of object of class Skyfield Time] list of time moments
    '''
    passes = []
    
    # Calculate the orbital period[minutes] of the satellite relative to the rotating earth
    P = 2*np.pi/(sat.model.no - np.pi/(12*60)) 
    # Determine the time step[seconds]
    t_step = int(np.round(60*np.sqrt(P/120))) 
    t = t_list(ts,t_start,t_end,t_step)

    # Satellite position relative to the station in ICRS
    sat_site = (sat - site).at(t)
    alt_sat, az_sat, distance_sat = sat_site.altaz()
    sat_above_horizon = alt_sat.degrees > cutoff
    boundaries, = np.diff(sat_above_horizon).nonzero()
    
    if len(boundaries) == 0: return passes
        
    if sat_above_horizon[boundaries[0]]:
        boundaries = np.append(0,boundaries)
    if len(boundaries)%2 != 0:
        boundaries = np.append(boundaries,len(sat_above_horizon)-1)    
    boundaries = np.array(t[boundaries].utc_iso()).reshape(len(boundaries) // 2,2)
    seconds = TimeDelta(np.arange(t_step+1), format='sec')

    for rises,sets in boundaries:
        t_rise = ts.from_astropy(Time(rises)+seconds)
        sat_site = (sat - site).at(t_rise)
        alt, az, distance = sat_site.altaz()
        sat_above_horizon = alt.degrees > cutoff
        pass_rise = t_rise[sat_above_horizon][0]
        t_set = ts.from_astropy(Time(sets)+seconds)
        sat_site = (sat - site).at(t_set)
        alt, az, distance = sat_site.altaz()
        sat_above_horizon = alt.degrees > cutoff
        
        if sat_above_horizon[-1]:
            pass_set = t_set[sat_above_horizon][0]
        else:
            pass_set = t_set[sat_above_horizon][-1]   
        passes.append([pass_rise.utc_iso(),pass_set.utc_iso()])     
    return passes
"""
def eclipsed(sat,sun,earth,t):
    '''
    Determine if a satellite is in the earth shadow。

    Usage: shadow = eclipsed(sat,sun,earth,t)

    Inputs:
    sat -> [object of class Skyfield satellite] satellite from tle
    sun -> [object of class Skyfield planets] sun from JPL ephemeris, such as DE421 and DE430
    earth -> [object of class Skyfield planets] Earth from JPL ephemeris
    t -> [object of class Skyfield Time] time moment or a set of time moments;

    Outputs:
    shadow -> [bool or list of bool] If True, then the satellite is in earth shadow; if False, then outside the shadow. 
    '''
    # Satellite position relative to the geocenter in ICRS
    sat_geo = sat.at(t)
    sat_geo_xyz = sat_geo.position.km
    sat_geo_d = sat_geo.distance().km
    # Solar position relative to the geocenter in ICRS
    sun_geo = (earth).at(t).observe(sun).apparent()
    sun_geo_xyz = sun_geo.position.km
    sun_geo_d = sun_geo.distance().km
    
    Radius_sun = R_sun.to(u.km).value
    Radius_earth = R_earth.to(u.km).value
    
    SinPenumbra = (Radius_sun - Radius_earth)/sun_geo_d
    CosPenumbra = np.sqrt(1 - SinPenumbra**2)
    
    CosTheta = np.sum(sat_geo_xyz*sun_geo_xyz,axis=0)/(sun_geo_d*sat_geo_d)*CosPenumbra + (sat_geo_d/Radius_earth)*SinPenumbra
    shadow = CosTheta < -np.sqrt(sat_geo_d**2-Radius_earth**2)/sat_geo_d*CosPenumbra + (sat_geo_d/Radius_earth)*SinPenumbra
    return shadow
"""
def visible_pass(start_time,end_time,site,timezone=0,twilight='nautical',visible_duration=120):
    '''
    Calculate the visible time period of satellite transit.

    Usage: visible_pass(start_time,end_time,site,timezone=8)

    Inputs:
    start_time -> [str] start time, such as '2020-06-01 00:00:00'
    end_time -> [str] end time, such as '2020-07-01 00:00:00'
    site -> [list of str] geodetic coordinates of a station, such as ['25.03 N','102.80 E','1987.05']

    Parameters:
    timezone -> [int, optional, default=0] time zone; if 0, then UTC is used.
    twilight -> [str,int,or float, optional, default='nautical'] dark sign; if 'dark', then the solar cutoff angle is less than -18 degrees;
    if 'astronomical', then less than -12 degrees; if 'nautical', then less than -6 degrees; if 'civil', then less than -0.8333 degrees;
    alternatively, it also can be set to a specific number, for example, 4 degrees.
    visible_duration -> [int, optional, default=120] visible duration in seconds

    Outputs:
    VisiblePasses_bysat.csv -> csv-format file of visible passes in sort of satellite
    VisiblePasses_bydate.csv -> csv-format file of visible passes in sort of date
    xxxx.txt -> one-day prediction file for each satellite
    '''
    home = str(Path.home())
    direc_eph = home + '/src/skyfield-data/ephemeris/'
    direc_time = home + '/src/skyfield-data/time_data/'
    de430 = direc_eph + 'de430.bsp'

    load_eph = Loader(direc_eph)
    load_time = Loader(direc_time)

    # URL of DE430
    url = 'http://www.shareresearch.me/wp-content/uploads/2020/05/de430.bsp' 

    if not path.exists(de430):
        print('Downloading the JPL ephemeris de430.bsp',end=' ... ')
        urlretrieve(url, de430)
        print('Finished')

    ts = load_time.timescale()
    planets = load_eph('de430.bsp')
    
    # Output information about the time system file and ephemeris file
    print(load_time.log)
    print(load_eph.log)

    if twilight == 'dark':
        sun_alt_cutoff = -18
    elif twilight == 'astronomical':
        sun_alt_cutoff = -12
    elif twilight == 'nautical': 
        sun_alt_cutoff = -6
    elif twilight == 'civil':
        sun_alt_cutoff = -0.8333
    elif type(twilight) is int or type(twilight) is float:
        sun_alt_cutoff = twilight 
    else:
        raise Exception("twilight must be one of 'dark','astronomical','nautical','civil', or a number.")     

    dir_TLE = 'TLE/'
    dir_prediction = 'prediction/'
    sun,earth = planets['sun'],planets['earth']
    sats = load.tle_file(dir_TLE+'satcat_3le.txt')
    
    lon,lat,ele = site
    observer = Topos(lon, lat, elevation_m = float(ele)) 

    # local start time
    t_start = Time(start_time) - timezone*u.hour 
    # local end time
    t_end = Time(end_time) - timezone*u.hour 
                   
    fileList_prediction = glob(dir_prediction+'*')
    if path.exists(dir_prediction):
        for file in fileList_prediction:
            remove(file)
    else:
        mkdir(dir_prediction)
    

    filename0 = 'VisiblePasses_bysat.csv'  
    filename1 = 'VisiblePasses_bydate.csv'

    outfile0 = open(dir_prediction+filename0,'w')
    header = ['Start Time[UTC+' + str(timezone) +']','End Time[UTC+' + str(timezone) +']','NORADID', 'During[seconds]']
    outfile0.write('{},{},{},{}\n'.format(header[0],header[1],header[2],header[3]))

    for sat in sats:
        visible_flag = False
        noradid = sat.model.satnum
        passes = next_pass(ts,t_start,t_end,sat,observer)
        if not passes: 
            continue
        else:
            outfile = open(dir_prediction+ str(noradid) + '.txt','w')
            outfile.write('# {:18s} {:8s} {:8s} {:8s} {:8s} {:10s} {:14s} {:7s} \n'.format('Date and Time(UTC)','Alt[deg]','Az[deg]','Ra[h]','Dec[deg]','Range[km]','Solar Alt[deg]','Visible'))
            
        for pass_start,pass_end in passes:
            t = t_list(ts,Time(pass_start),Time(pass_end),1)
            sat_observer = (sat - observer).at(t)
            sat_alt, sat_az, sat_distance = sat_observer.altaz()
            sat_ra, sat_dec, sat_distance = sat_observer.radec() 
            sun_observer = (earth+observer).at(t).observe(sun).apparent()
            sun_alt, sun_az, sun_distance = sun_observer.altaz()
            sun_beneath = sun_alt.degrees < sun_alt_cutoff 
            #shadow = eclipsed(sat,sun,earth,t) 
            sunlight = sat.at(t).is_sunlit(planets)
            # Under the premise of satellite transit, visibility requires at least two conditions to be met: dark and outside the earth shadow.
            #visible = sun_beneath & ~shadow
            visible = sun_beneath & sunlight
        
            if visible.any():
                visible_flag = True
                t_visible = np.array(t.utc_iso())[visible]
                t_visible_0 = (Time(t_visible[0])+timezone*u.hour).iso
                t_visible_1 = (Time(t_visible[-1])+timezone*u.hour).iso
                during = round((Time(t_visible[-1]) - Time(t_visible[0])).sec)
                if during >= visible_duration:
                    outfile0.write('{:s},{:s},{:d},{:d}\n'.format(t_visible_0,t_visible_1,noradid,during))
            
            # Generate a one-day prediction file
            if Time(pass_end) < t_start + 1: 
                for i in range(len(t)):
                    outfile.write('{:20s} {:>8.4f} {:>8.4f} {:>8.5f} {:>8.4f} {:>10.4f} {:>10.4f} {:>7d} \n'.format(t.utc_strftime('%Y-%m-%d %H:%M:%S')[i],sat_alt.degrees[i],sat_az.degrees[i],sat_ra.hours[i],sat_dec.degrees[i],sat_distance.km[i],sun_alt.degrees[i],visible[i]))
                outfile.write('\n')
        
            '''
            # Generate a one-day prediction in visibility period
            if visible.any():
                t_visible = np.array(t.utc_iso())[visible]
                for i in range(len(t_visible)):
                    outfile.write('{:20s} {:>8.4f} {:>8.4f} {:>8.5f} {:>8.4f} {:>10.4f} \n'.format(t_visible[i],sat_alt.degrees[visible][i],sat_az.degrees[visible][i],sat_ra.hours[visible][i],sat_dec.degrees[visible][i],sat_distance.km[visible][i]))
                outfile.write('\n')
            ''' 
        if not visible_flag:
            outfile0.write('{:s},{:s},{:d}\n\n'.format('','',noradid))
        else:
            outfile0.write('\n')
        outfile.close()
    outfile0.close() 
    
    # Sort satellites according to the start time of the visible time period
    dates,temp = [],[]
    VisiblePasses = pd.read_csv(dir_prediction+filename0,dtype=object)
    for date in VisiblePasses[header[0]]:
        if str(date) != 'nan': dates.append(date[:10])
    dates = np.sort(list(set(dates))) 
    for date in dates:
        date_flag = VisiblePasses[header[0]].str.contains(date,na=False)
        temp.append(VisiblePasses[date_flag].sort_values(by=[header[0]]).append(pd.Series(dtype=object), ignore_index=True)) 
    pd.concat(temp).to_csv(dir_prediction+'VisiblePasses_bydate.csv',index=False,mode='w')
    print('Complete the calculation of the visible time period of satellite transit.')    