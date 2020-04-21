from os import system,path,makedirs

from ..cpf_utils.cpf_interpolate import cpf_interpolate,itrs2horizon

class CPFdata(object):
    '''
    class CPFdata

        - attributes:
            - info: all information about the cpf ephemeris file
            - version: version number of the cpf ephemeris, usually 1.0 
            - ephemeris_source: source of the cpf ephemeris file, such as JAX and SGF
            - time_ephemeris: production time of the cpf ephemeris
            - target_name: target name, such as lageos1
            - cospar_id: COSPAR ID of taeget
            - norad_id: NORAD ID of target

        - methods:
            - pred: predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of the station
    '''
    
    def __init__(self,data):

        version = []
        ephemeris_source,time_ephemeris = [],[]
        target_name,cospar_id,norad_id = [],[],[]
        
        for cpf_data in data:
            version.append(cpf_data['Format Version'])
            ephemeris_source.append(cpf_data['Ephemeris Source'])
            time_ephemeris.append(cpf_data['Time of Ephemeris Production'])
            target_name.append(cpf_data['Target Name'])
            cospar_id.append(cpf_data['COSPAR ID'])
            norad_id.append(cpf_data['NORAD ID']) 

        self.info = data
        self.version = version
        self.ephemeris_source = ephemeris_source
        self.time_ephemeris = time_ephemeris
        self.target_name = target_name
        self.cospar_id = cospar_id
        self.norad_id = norad_id

    def __repr__(self):
    
        return 'instance of class CPFdata'

    def pred(self,station,t_start,t_end,t_increment,coord_type='geodetic',mode='apparent'):
        '''
        Predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of the station.

        Usage:
        cpf_data.pred(station,t_start,t_end,t_increment)
        cpf_data.pred(station,t_start,t_end,t_increment,'geocentric')
        cpf_data.pred(station,t_start,t_end,t_increment,'geocentric','geometric')

        Inputs:
        station -> [numercial array or list with 3 elements] coordinates of station. It can either be geocentric(x, y, z) coordinates or geodetic(lon, lat, height) coordinates.
        Unit for (x, y, z) are meter, and for (lon, lat, height) are degree and meter.
        t_start -> [str] starting date and time for prediction, such as '2016-12-31 20:06:40'
        t_end -> [str] ending date and time for prediction, such as '2017-01-01 03:06:40'
        t_increment -> [int or float] time increment for prediction, such as 0.5, 1, 2 etc.; unit is in second

        Parameters:
        coord_type -> [optional, str, default = 'geodetic'] coordinates type for coordinates of station; it can either be 'geocentric' or 'geodetic'.
        mode -> [optional, str, default = 'apparent']  whether to consider the light time; if 'geometric', instantaneous position vector from station to target is computed; 
        if 'apparent', position vector containing light time from station to target is computed.

        Outputs:
        pred/target_name.txt -> [str] output prediction file with filename of target_name in directory pred
        Note: (1) If the mode is 'geometric', then the transmitting direction of the laser coincides with the receiving direction at a certain moment. 
        In this case, the output prediction file will not contain the difference between the receiving direction and the transmitting direction.
        If the mode is 'apparent', then the transmitting direction of the laser is inconsistent with the receiving direction at a certain moment. 
        In this case, the output prediction file will contain the difference between the receiving direction and the transmitting direction.
        (2) The 10-point(degree 9) Lagrange polynomial interpolation method is used to interpolate the cpf ephemeris.
        (3) The influence of leap second is considered in the prediction generation.
        '''

        dir_pred_to = 'pred/'
        if not path.exists(dir_pred_to): 
            makedirs(dir_pred_to)   
        else:
            system('rm -rf %s/*' % dir_pred_to)

        data = self.info

        for cpf_data in data:
            target = cpf_data['Target Name']
            predfile = open(dir_pred_to+target+'.txt','w')

            ts_utc_cpf = cpf_data['ts_utc']
            ts_mjd_cpf = cpf_data['MJD']
            ts_sod_cpf = cpf_data['SoD']
            positions_cpf = cpf_data['positions[m]']
            leap_second_cpf = cpf_data['Leap_Second']

            if mode == 'geometric': 
                ts,ts_mjd,ts_sod,az,alt,r,tof1 = cpf_interpolate(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment,mode,station,coord_type)

                n = len(ts)    

                for i in range(n):
                    predfile.write('{:19s}  {:5d}  {:11.5f}  {:9.5f}  {:9.5f}  {:13.3f}  {:12.10f}\n'.format(ts[i],ts_mjd[i],ts_sod[i],az[i],alt[i],r[i],tof1[i]))
                predfile.close()

            elif mode == 'apparent':
                ts,ts_mjd,ts_sod,az_trans,alt_trans,delta_az,delta_alt,r_trans,tof2 = cpf_interpolate(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment,mode,station,coord_type)

                n = len(ts)    

                for i in range(n): 
                    predfile.write('{:19s}  {:5d}  {:11.5f}  {:9.5f}  {:9.5f}  {:8.5f}  {:8.5f}  {:13.3f}  {:12.10f}\n'.format(ts[i],ts_mjd[i],ts_sod[i],az_trans[i],alt_trans[i],delta_az[i],delta_alt[i],r_trans[i],tof2[i]))
                predfile.close()

            else:
                raise Exception("Mode must be 'geometric' or 'apparent'.")