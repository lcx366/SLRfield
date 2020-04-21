'''
slrfield slrclasses subpackage

This subpackage defines some classes that facilitate the processing of the SLR(Satellite Laser Ranging) data.

#========================== cpfpred ========================#

Class structure:

    CPFdata

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