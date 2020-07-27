import numpy as np
from astropy.time import Time,TimeDelta

from ..slrclasses.cpfpred import CPFdata

def read_cpf(cpf_file):
    '''
    Parse a single CPF ephemeris file and read the data.

    Usage: 
    data = read_cpf(cpf_file)

    Inputs:
    cpf_file -> [str] the name of CPF ephemeris file, such as 'ajisai_cpf_170829_7411.hts'

    Outputs:
    data -> [dictionary] a python dictionary containing the main information of the CPF ephemeris file. 
    The information includes the following contents:
    (1) Format; (2) Format Version (3) Ephemeris Source (4) date of ephemeris production (5) Ephemeris Sequence number
    (6) Target name (7) COSPAR ID (8) SIC (9) NORAD ID (10) Starting date and time (11) Ending date and time
    (12) Time between table entries (UTC seconds) (13) Target type (14) Reference frame (15) Rotational angle type
    (16) Center of mass correction (17) Direction type (18) Modified Julian Date (19) Seconds of Day (20) Leap_Second
    (21) time in UTC (22) target positions in meters
    '''
    cpf_data = open(cpf_file,'r').readlines()
    data = {'MJD':[],'SoD':[],'positions[m]':[],'Leap_Second':[]}
    for line in cpf_data:
        info = line.split()
        if info[0] == 'H1':
            data['Format'] = info[1]
            data['Format Version'] = info[2]
            data['Ephemeris Source'] = info[3]
            data['Time of Ephemeris Production'] = Time('-'.join(info[4:7])+' '+':'.join([info[7],'0','0'])).iso
            data['Ephemeris Sequence Number'] = info[8]
            data['Target Name'] = info[9]
        elif info[0] == 'H2':
            data['COSPAR ID'] = info[1]
            data['SIC'] = info[2]
            data['NORAD ID'] = info[3]
            data['Start'] = Time('-'.join(info[4:7])+' '+':'.join(info[7:10])).iso
            data['End'] = Time('-'.join(info[10:13])+' '+':'.join(info[13:16])).iso
            data['Time Interval[sec]'] = info[16]
            
            if info[17] == '1':
                target_type = 'passive(retro-reflector) artificial satellite'
            elif info[17] == '2':
                target_type = 'passive(retro-reflector) lunar reflector'
            elif info[17] == '3':
                target_type = 'synchronous transponder'
            elif info[17] == '4':
                target_type = 'asynchronous transponder'
            else:
                raise Exception('Unknown target type')
            data['Target Type'] = target_type   
            
            if info[19] == '0':
                reference_frame = 'ITRF(default)'
            elif info[19] == '1':
                reference_frame = 'GCRF(True of Date)'
            elif info[19] == '2':
                reference_frame = 'GCRF(Mean of Date J2000.0)'
            else:
                raise Exception('Unknown reference frame type')
            data['Reference Frame'] = reference_frame    
            
            if info[20] == '0':
                rotational_angle = 'Not Applicable'
            elif info[20] == '1':
                rotational_angle = 'Lunar Euler angles: φ, θ, and ψ'
            elif info[20] == '2':
                rotational_angle = 'North pole Right Ascension and Declination, and angle to prime meridian (α0, δ0, and W)'
            else:
                raise Exception('Unknown rotational angle type')
            data['Rotational Angle'] = rotational_angle   
            
            if info[21] == '0':
                CM_correction = 'None applied. Prediction is for center of mass of target'
            elif info[21] == '1':
                CM_correction = 'Applied. Prediction is for retro-reflector array'
            else:
                raise Exception('Unknown center of mass correction type')
            data['Center of Mass Correction'] = CM_correction          

        elif info[0] == '10':
            direction_flag = info[1]
            data['MJD'].append(info[2])  
            data['SoD'].append(info[3])
            data['Leap_Second'].append(info[4])
            data['positions[m]'].append(info[5:8])
        else:
            pass
        
    if direction_flag == '0':
        direction = 'instantaneous vector from geocenter to target, without light-time iteration'
    elif direction_flag == '1':
        direction = 'position vector from geocenter to target with light-time iteration at the transmit epoch'
    elif direction_flag == '2':
        direction = 'position vector from target to geocenter with light-time iteration at the receive epoch'
    else:
        raise Exception('Unknown direction flag')
    data['Direction'] = direction
            
    data['MJD'],data['SoD'] = np.array(data['MJD'],dtype = int),np.array(data['SoD'],dtype = float)
    data['Leap_Second'] = np.array(data['Leap_Second'],dtype = int)
    data['positions[m]'] = np.array(data['positions[m]'],dtype = float)
    data['ts_utc'] = (Time(data['MJD'],format = 'mjd') + TimeDelta(data['SoD'],format='sec')).iso

    return data

def read_cpfs(cpf_files):
    '''
    Parse a single CPF ephemeris file of a set of CPF ephemeris files and read the data.

    Usage: 
    cpf_data = read_cpfs(cpf_files)

    Inputs:
    cpf_files -> [str] name of CPF ephemeris file, such as 'ajisai_cpf_170829_7411.hts'; 
    or list of filenames, such as ['CPF/EDC/2016-12-31/starlette_cpf_161231_8661.sgf','CPF/CDDIS/2020-04-15/lageos1_cpf_200415_6061.jax']

    Outputs:
    cpf_data -> [object] instance of class CPFdata
    '''
    data = []

    if type(cpf_files) is str: cpf_files = [cpf_files]

    for cpf_file in cpf_files:
        data.append(read_cpf(cpf_file))

    return CPFdata(data)     
