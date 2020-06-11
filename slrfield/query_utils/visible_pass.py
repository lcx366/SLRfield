from glob import glob
from pathlib import Path
from os import path,mkdir,remove
from urllib.request import urlretrieve,ContentTooShortError
from wget import download

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
    ts -> [Skyfield time scale] Skyfield time scale system; it is constitutive of 'deltat.data', 'deltat.preds', and 'Leap_Second.dat'
    t_start -> [object of class Astropy Time] Start time, such as Time('2020-06-01 00:00:00')
    t_end -> [object of class Astropy Time] End time, such as Time('2020-06-30 00:00:00') 

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
    Generate the space target passes in a time period.

    Usage: 
    passes = next_pass(ts,t_start,t_end,sat,site,cutoff)

    Inputs:
    ts -> [Skyfield time scale] Skyfield time scale system; it is constitutive of 'deltat.data', 'deltat.preds', and 'Leap_Second.dat'
    t_start -> [object of class Astropy Time] Start time, such as Time('2020-06-01 00:00:00')
    t_end -> [object of class Astropy Time] End time, such as Time('2020-06-30 00:00:00') 
    sat -> [object of class Skyfield satellite] Space target
    site -> [object of class Skyfield Topos] Station

    Parameters:
    cutoff -> [float, optional, default=10] Cutoff altitude angle

    Outputs:
    t -> [list of object of class Skyfield Time] List of time moments
    '''
    passes = []
    
    # Approximately calculate the orbital period[minutes] of a target relative to the rotating Earth
    P = 2*np.pi/(sat.model.no - np.pi/(12*60)) 
    # Determine the time step[seconds]
    t_step = int(np.round(60*np.sqrt(P/120))) 
    t = t_list(ts,t_start,t_end,t_step)

    # Calculate the target position relative to the station in ICRS
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

def visible_pass(start_time,end_time,site,timezone=0,cutoff=10,twilight='nautical',visible_duration=120):
    '''
    Generate the visible passes of space targets in a time period.

    Usage: 
    visible_pass(start_time,end_time,site,timezone=8)

    Inputs:
    start_time -> [str] start time, such as '2020-06-01 00:00:00'
    end_time -> [str] end time, such as '2020-07-01 00:00:00'
    site -> [list of str] geodetic coordinates of a station, such as ['21.03 N','157.80 W','1987.05']

    Parameters:
    timezone -> [int, optional, default=0] time zone, such as -10; if 0, then UTC is used.
    cutoff -> [float, optional, default=10] Satellite Cutoff Altitude Angle
    twilight -> [str, or float, optional, default='nautical'] Dark sign or solar cutoff angle; if 'dark', then the solar cutoff angle is less than -18 degrees;
    if 'astronomical', then less than -12 degrees; if 'nautical', then less than -6 degrees; if 'civil', then less than -0.8333 degrees;
    alternatively, it also can be set to a specific number, for example, 4.0 degrees.
    visible_duration -> [int, optional, default=120] Duration[seconds] of a visible pass

    Outputs:
    VisiblePasses_bysat.csv -> csv-format files that record visible passes in sort of target
    VisiblePasses_bydate.csv -> csv-format files that record visible passes in sort of date
    xxxx.txt -> one-day prediction files for targets
    '''
    home = str(Path.home())
    direc_eph = home + '/src/skyfield-data/ephemeris/'
    direc_time = home + '/src/skyfield-data/time_data/'
    de430 = direc_eph + 'de430.bsp'

    load_eph = Loader(direc_eph)
    load_time = Loader(direc_time)

    print('\nDownloading JPL ephemeris DE430 and timescale files',end=' ... \n')

    # URL of JPL DE430
    url = 'http://www.shareresearch.me/wp-content/uploads/2020/05/de430.bsp' 
    '''
    url = 'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp'
    url = 'https://repos.cosmos.esa.int/socci/projects/SPICE_KERNELS/repos/juice/browse/kernels/spk/de430.bsp'
    '''
    if not path.exists(de430):
        print('Downloading de430.bsp',end=' ... ')
        try:
            urlretrieve(url, de430)
            print('Finished')
        except ContentTooShortError:
            print('\nDownload failed using urlretrieve. Try to download using wget tool.')
            download(url, de430)  

    print('Downloading timescale files',end=' ... \n')
    ts = load_time.timescale()
    planets = load_eph('de430.bsp')
    
    # Print information about the time system file and ephemeris file
    print(load_time.log)
    print(load_eph.log)

    print('\nCalculating one-day predictions and multiple-day visible passes for targets', end=' ... \n')

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
    
    print('Generate one-day prediction for targets:')

    for sat in sats:
        visible_flag = False
        noradid = sat.model.satnum
        passes = next_pass(ts,t_start,t_end,sat,observer,cutoff)
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
                    outfile0.write('{:s},{:s},{:d},{:d}\n'.format(t_visible_0,t_visible_1,noradid,int(during)))
            
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
        print(noradid)
    outfile0.close() 
    print('Generate multiple-day visible passes for all targets.')
    
    # Sort by the start time of the visible passes
    dates,temp = [],[]
    VisiblePasses = pd.read_csv(dir_prediction+filename0,dtype=object)
    for date in VisiblePasses[header[0]]:
        if str(date) != 'nan': dates.append(date[:10])
    dates = np.sort(list(set(dates))) 
    for date in dates:
        date_flag = VisiblePasses[header[0]].str.contains(date,na=False)
        temp.append(VisiblePasses[date_flag].sort_values(by=[header[0]]).append(pd.Series(dtype=object), ignore_index=True)) 
    if not temp:
        print('No visible passes are found!')
    else:    
        pd.concat(temp).to_csv(dir_prediction+'VisiblePasses_bydate.csv',index=False,mode='w')
    print('Over!')    
