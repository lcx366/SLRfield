from os import system,path,makedirs,walk

from ..cpf.cpf_interpolate import cpf_interp_azalt,cpf_interp_xyz,next_pass_horizon
from ..cpf.cpf_read import read_cpf

class CPF(object):
    """
    class CPF
    """
    
    def __init__(self,data,cpf_dir):

        version = []
        eph_source,time_eph,start_end_eph = [],[],[]
        target_name,cospar_id,norad_id = [],[],[]
        
        for cpf_data in data:
            version.append(cpf_data['Format Version'])
            eph_source.append(cpf_data['Ephemeris Source'])
            time_eph.append(cpf_data['Time of Ephemeris Production'])
            start_end_eph.append(cpf_data['Start']+'->'+cpf_data['End'])
            target_name.append(cpf_data['Target Name'])
            cospar_id.append(cpf_data['COSPAR ID'])
            norad_id.append(cpf_data['NORAD ID'])     

        self.info = data
        self.version = version
        self.eph_source = eph_source
        self.time_eph = time_eph
        self.target_name = target_name
        self.cospar_id = cospar_id
        self.norad_id = norad_id
        self.eph_dir = cpf_dir

    def __repr__(self):
    
        return 'instance of class CPF'

    def from_files(cpf_dir,cpf_files=None):
        """
        Parse a single CPF ephemeris file of a set of CPF ephemeris files and read the data.

        Inputs:
            cpf_dir -> [str] Directory for storing CPF ephemeris files

        Parameters:    
            cpf_files -> [str,list of str,default=None] name of CPF ephemeris file, such as 'ajisai_cpf_170829_7411.hts'; 
            or list of filenames, such as ['CPF/EDC/2016-12-31/starlette_cpf_161231_8661.sgf','CPF/CDDIS/2020-04-15/lageos1_cpf_200415_6061.jax'];
            if None, all CPF ephemeris files in CPF directory will be loaded.

        Outputs:
            cpf_data  -> [object] instance of class CPF
        """
        data = []

        if cpf_files is None:
            for (_, _, cpf_files) in walk(cpf_dir): pass
        elif type(cpf_files) is str: 
            cpf_files = [cpf_files]

        for cpf_file in cpf_files:
            data.append(read_cpf(cpf_dir,cpf_file))

        return CPF(data,cpf_dir)

    def pred_xyz(self,t_start,t_end,t_increment,keep=True):    
        """
        Predict the cartesian coordinates of the target in GCRF.

        Usage:
            cpf_data.pred_xyz(t_start,t_end,t_increment)
            cpf_data.pred_xyz(t_start,t_end,t_increment,keep=False)

        Inputs:
            t_start -> [str] starting date and time for prediction, such as '2016-12-31 20:06:40'
            t_end -> [str] ending date and time for prediction, such as '2017-01-01 03:06:40'
            t_increment -> [int or float] time increment for prediction, such as 0.5, 1, 2 etc.; unit is in second

        Parameters:
            keep -> [bool, default = True] whether or not keep the prediction files in the storing directory.

        Outputs:
            target_name.txt -> [str] output prediction file with filename of target_name in directory pred
            Note:
            (1) The 10-point(degree 9) Lagrange polynomial interpolation method is used to interpolate the cpf ephemeris.
            (2) The influence of leap second is considered in the prediction generation.
        """

        dir_pred_to = 'pred/xyz'+self.eph_dir.split('CPF')[1]
        if not path.exists(dir_pred_to): makedirs(dir_pred_to)   
        if not keep: system('rm -rf %s/*' % dir_pred_to)     

        data = self.info

        for cpf_data in data:
            target = cpf_data['Target Name']
            predfile = open(dir_pred_to+target+'.txt','w')

            ts_utc_cpf = cpf_data['ts_utc']
            ts_mjd_cpf = cpf_data['MJD']
            ts_sod_cpf = cpf_data['SoD']
            positions_cpf = cpf_data['positions[m]']
            leap_second_cpf = cpf_data['Leap_Second']

            ts,ts_mjd,ts_sod,x,y,z = cpf_interp_xyz(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_increment)

            n = len(ts)  
            predfile.write('{:^24s}  {:^5s}  {:^11s}  {:^13s}  {:^13s}  {:^13s}\n'.format('UTC','MJD','SOD','x[m]','y[m]','z[m]'))  
            for i in range(n):
                predfile.write('{:24s}  {:5d}  {:11.5f}  {:13.3f}  {:13.3f}  {:13.3f}\n'.format(ts[i]+'Z',ts_mjd[i],ts_sod[i],x[i],y[i],z[i]))
            predfile.close()  

    def pred_azalt(self,station,t_start,t_end,t_increment,coord_type='geodetic',cutoff=10,mode='apparent',keep=True):
        """
        Predict the azimuth, altitude, distance of the target, and the time of flight for laser pulse etc. given the coordinates of the station.

        Usage:
            cpf_data.pred_azalt(station,t_start,t_end,t_increment)
            cpf_data.pred_azalt(station,t_start,t_end,t_increment,'geocentric')
            cpf_data.pred_azalt(station,t_start,t_end,t_increment,'geocentric','geometric')

        Inputs:
            station -> [numercial array or list with 3 elements] coordinates of station. It can either be geocentric(x, y, z) coordinates or geodetic(lon, lat, height) coordinates.
            Unit for (x, y, z) are meter, and for (lon, lat, height) are degree and meter.
            t_start -> [str] starting date and time for prediction, such as '2016-12-31 20:06:40'
            t_end -> [str] ending date and time for prediction, such as '2017-01-01 03:06:40'
            t_increment -> [int or float] time increment for prediction, such as 0.5, 1, 2 etc.; unit is in second

        Parameters:
            coord_type -> [str, default = 'geodetic'] coordinates type for coordinates of station; it can either be 'geocentric' or 'geodetic'.
            cutoff -> [float,default = 10] altitude cut-off angle
            mode -> [str, default = 'apparent']  whether to consider the light time; if 'geometric', instantaneous position vector from station to target is computed; 
            if 'apparent', position vector containing light time from station to target is computed.

        Outputs:
            target_name.txt -> [str] output prediction file with filename of target_name in directory pred
            Note: (1) If the mode is 'geometric', then the transmitting direction of the laser coincides with the receiving direction at a certain moment. 
            In this case, the output prediction file will not contain the difference between the receiving direction and the transmitting direction.
            If the mode is 'apparent', then the transmitting direction of the laser is inconsistent with the receiving direction at a certain moment. 
            In this case, the output prediction file will contain the difference between the receiving direction and the transmitting direction.
            (2) The 10-point(degree 9) Lagrange polynomial interpolation method is used to interpolate the cpf ephemeris.
            (3) The influence of leap second is considered in the prediction generation.
        """
        dir_pred_to = 'pred/azalt'+self.eph_dir.split('CPF')[1]
        if not path.exists(dir_pred_to): makedirs(dir_pred_to)   
        if not keep: system('rm -rf %s/*' % dir_pred_to)

        data = self.info

        for cpf_data in data:
            target = cpf_data['Target Name']
            ts_utc_cpf = cpf_data['ts_utc']
            ts_mjd_cpf = cpf_data['MJD']
            ts_sod_cpf = cpf_data['SoD']
            positions_cpf = cpf_data['positions[m]']
            leap_second_cpf = cpf_data['Leap_Second']

            t_step = (ts_sod_cpf[1] - ts_sod_cpf[0])//6
            passes = next_pass_horizon(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start,t_end,t_step,station,coord_type,cutoff)

            j = 1
            for t_start_pass,t_end_pass in passes:
                predfile = open('{:s}{:s}_{:d}.txt'.format(dir_pred_to,target,j),'w') 
                if mode == 'geometric': 
                    ts,ts_mjd,ts_sod,az,alt,r,tof1 = cpf_interp_azalt(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start_pass,t_end_pass,t_increment,mode,station,coord_type)
                    predfile.write('{:^24s}  {:^5s}  {:^11s}  {:^9s}  {:^9s}  {:^13s}  {:^12s}\n'.format('UTC','MJD','SOD','Az[deg]','Alt[deg]','Distance[m]','TOF[s]'))  
                    for i in range(len(ts)):
                        predfile.write('{:24s}  {:5d}  {:11.5f}  {:9.5f}  {:9.5f}  {:13.3f}  {:12.10f}\n'.format(ts[i]+'Z',ts_mjd[i],ts_sod[i],az[i],alt[i],r[i],tof1[i]))

                elif mode == 'apparent':
                    ts,ts_mjd,ts_sod,az_trans,alt_trans,delta_az,delta_alt,r_trans,tof2 = cpf_interp_azalt(ts_utc_cpf,ts_mjd_cpf,ts_sod_cpf,leap_second_cpf,positions_cpf,t_start_pass,t_end_pass,t_increment,mode,station,coord_type)
                    predfile.write('{:^24s}  {:^5s}  {:^11s}  {:^9s}  {:^9s}  {:^8s}  {:^8s}  {:^13s}  {:^12s}\n'.format('UTC','MJD','SOD','Az[deg]','Alt[deg]','dAz[deg]','dAlt[deg]','Distance[m]','TOF[s]'))  
                    for i in range(len(ts)): 
                        predfile.write('{:24s}  {:5d}  {:11.5f}  {:9.5f}  {:9.5f}  {:8.5f}  {:8.5f}  {:13.3f}  {:12.10f}\n'.format(ts[i]+'Z',ts_mjd[i],ts_sod[i],az_trans[i],alt_trans[i],delta_az[i],delta_alt[i],r_trans[i],tof2[i]))
                else:
                    raise Exception("Mode must be 'geometric' or 'apparent'.") 
                predfile.close()  
                j+=1      
