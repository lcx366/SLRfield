import numpy as np
import pandas as pd
from os import path,makedirs,remove
from pathlib import Path
import requests
from urllib.request import urlretrieve
from datetime import datetime,timedelta

def discos_query(COSPARID=None,NORADID=None,ObjectClass=None,Decayed=None,DecayDate=None,Mass=None,RCSMin=None,RCSMax=None,RCSAvg=None,sort=None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the DISCOS database.

    Usage: 
    df = discos_query(Decayed=False,RCSAvg=[5,15])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target ID by the in Committee On SPAce Research; If None, then this option is ignored. 
    NORADID -> [int, str, list of int, or list of str, optional, default = None] Target ID by the North American Aerospace Defense Command; If None, then this option is ignored.
    ObjectClass -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris',Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, then this option is ignored.  
    Decayed ->  [bool, optional, default = None], also called reentry; If False, targets are still in orbit; if True, then reentry; if None, then this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    Mass -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; must be in form of [mass1,mass2], such as [5.0,10.0]; if None, then this option is ignored.
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, then this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Mimimum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, then this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [5,20]; if None, then this option is ignored.
    sort -> [str, optional, default = None] way of sorting, such as sort by mass; if None, then sort by NORADID defautly.
    outfile -> [bool, optional, default = True] If True, then a csv-formatted file named 'discos_catalog' is created; if False, then no files are generated.
    
    Outputs:
    df -> pandas dataframe
    discos_catalog.csv -> [optional] a csv-formatted file that records the pandas dataframe
    '''
    # DISCOS tokens
    home = str(Path.home())
    direc = home + '/src/discos-data/'
    tokenfile = direc + 'discos-token'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(tokenfile):
        token = input('Please input the DISCOS tokens(which can be achieved from https://discosweb.esoc.esa.int/tokens): ')
        outfile = open(tokenfile,'w')
        outfile.write(token)
        outfile.close()
    else:
        infile = open(tokenfile,'r')
        token = infile.readline()
        infile.close()
    
    URL = 'https://discosweb.esoc.esa.int'
    params = {}
    
    if ObjectClass is not None:
        if type(ObjectClass) is str:
            params['filter'] = "eq(objectClass,'{:s}')".format(ObjectClass)
        elif type(ObjectClass) is list:
            params_filter = []
            for element in ObjectClass:
                params_filter.append("eq(objectClass,'{:s}')".format(element))
            params['filter'] = '|'.join(params_filter)
            params['filter'] = '(' + params['filter'] + ')'
        else:
            raise Exception('Type of ObjectClass should be either string or list.')
            
    # Filter parameters for 'Decayed' 
    if Decayed is not None:
        if Decayed is False:
            if 'filter' in params.keys():
                params['filter'] += "&(eq(reentry.epoch,null))"
            else:
                params['filter'] = "eq(reentry.epoch,null)"
        elif Decayed is True:
            if 'filter' in params.keys():
                params['filter'] += "&(ne(reentry.epoch,null))"
            else:
                params['filter'] = "ne(reentry.epoch,null)"
        else:
            raise Exception("'Decayed' must be one of 'False', 'True', or 'None'.")   
            
    # Filter parameters for 'DecayDate'
    if DecayDate is not None:
        if 'filter' in params.keys():
            params['filter'] += "&(gt(reentry.epoch,epoch:'{:s}')&lt(reentry.epoch,epoch:'{:s}'))".format(DecayDate[0],DecayDate[1])
        else:
            params['filter'] = "gt(reentry.epoch,epoch:'{:s}')&lt(reentry.epoch,epoch:'{:s}')".format(DecayDate[0],DecayDate[1])
    
    # Filter parameters for 'COSPARID'
    if COSPARID is not None:
        if 'filter' in params.keys():
            if type(COSPARID) is str:
                params['filter'] += "&(eq(cosparId,'{:s}'))".format(COSPARID)
            elif type(COSPARID) is list:    
                params['filter'] += '&(in(cosparId,{:s}))'.format(str(tuple(COSPARID))).replace(' ', '')
            else:
                raise Exception('Type of COSPARID should be in str or list of str.')
        else:
            if type(COSPARID) is str:
                params['filter'] = "eq(cosparId,'{:s}')".format(COSPARID)
            elif type(COSPARID) is list:    
                params['filter'] = 'in(cosparId,{:s})'.format(str(tuple(COSPARID))).replace(' ', '')
            else:
                raise Exception('Type of COSPARID should be in str or list of str.')
            
    # Filter parameters for 'NORADID'        
    if NORADID is not None:
        if 'filter' in params.keys():
            if type(NORADID) is int:
                params['filter'] += '&(eq(satno,{:d}))'.format(NORADID)   
            elif type(NORADID) is str:
                params['filter'] += '&(eq(satno,{:s}))'.format(NORADID)
            elif type(NORADID) is list:    
                params['filter'] += '&(in(satno,{:s}))'.format(str(tuple(NORADID))).replace(' ', '')
            else:
                raise Exception('Type of NORADID should be in int, str, list of int, or list of str.')  
        else:
            if type(NORADID) is int:
                params['filter'] = 'eq(satno,{:d})'.format(NORADID)   
            elif type(NORADID) is str:
                params['filter'] = 'eq(satno,{:s})'.format(NORADID)
            elif type(NORADID) is list:    
                params['filter'] = 'in(satno,{:s})'.format(str(tuple(NORADID))).replace(' ', '')
            else:
                raise Exception('Type of NORADID should be in int, str, list of int, or list of str.') 
            
    # Filter parameters for 'RCSMin'            
    if RCSMin is not None:
        if 'filter' in params.keys():
            params['filter'] += '&(gt(xSectMin,{:.4f})&lt(xSectMin,{:.4f}))'.format(RCSMin[0],RCSMin[1])
        else:
            params['filter'] = 'gt(xSectMin,{:.4f})&lt(xSectMin,{:.4f})'.format(RCSMin[0],RCSMin[1])
            
    # Filter parameters for 'RCSMax'     
    if RCSMax is not None:
        if 'filter' in params.keys():
            params['filter'] += '&(gt(xSectMax,{:.4f})&lt(xSectMax,{:.4f}))'.format(RCSMax[0],RCSMax[1])  
        else:
            params['filter'] = 'gt(xSectMax,{:.4f})&lt(xSectMax,{:.4f})'.format(RCSMax[0],RCSMax[1])
            
    # Filter parameters for 'RCSAvg'     
    if RCSAvg is not None:
        if 'filter' in params.keys():
            params['filter'] += '&(gt(xSectAvg,{:.4f})&lt(xSectAvg,{:.4f}))'.format(RCSAvg[0],RCSAvg[1]) 
        else:
            params['filter'] = 'gt(xSectAvg,{:.4f})&lt(xSectAvg,{:.4f})'.format(RCSAvg[0],RCSAvg[1])
    
    # sort        
    if sort is None:    
        params['sort'] = 'satno'  
    else:
        pass

    # Initialize the page parameter 
    params['page[number]'] = 1
    extract = []
    
    while True:
        params['page[size]'] = 100 # Number of entries for each page   
        response = requests.get(f'{URL}/api/objects',headers = {'Authorization': f'Bearer {token}'},params = params)
        doc = response.json()

        if response.ok:
            data = doc['data']
            for element in data:
                extract.append(element['attributes'])
            currentPage = doc['meta']['pagination']['currentPage']
            totalPages = doc['meta']['pagination']['totalPages']
            
            print('CurrentPage {:3d} in TotalPages {:3d}'.format(currentPage,totalPages))
            
            if currentPage < totalPages: 
                params['page[number]'] += 1
            else:
                break
        else:
            return doc['errors']
    
    # Change the name of the column and readjust the order of the column    
    old_column = ['height', 'xSectMax', 'name', 'satno', 'vimpelId', 'objectClass','mass', 'xSectMin', 'depth', 'xSectAvg', 'length', 'shape', 'cosparId']
    new_column = ['Height[m]', 'RCSMax[m2]', 'Satellite Name', 'NORADID', 'VimpelId', 'ObjectClass', 'Mass[kg]', 'RCSMin[m2]', 'Depth[m]', 'RCSAvg[m2]', 'Length[m]', 'Shape', 'COSPARID']
    new_column_reorder = ['COSPARID', 'NORADID', 'VimpelId', 'Satellite Name','ObjectClass','Mass[kg]','Shape','Height[m]','Length[m]','Depth[m]','RCSMin[m2]','RCSMax[m2]','RCSAvg[m2]']
    df = pd.DataFrame.from_dict(extract,dtype=object).rename(columns=dict(zip(old_column, new_column)), errors='raise')
    df = df.reindex(columns=new_column_reorder) 
    if outfile: df.to_csv('discos_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df   

def download_satcat():
    '''
    Download or update the satellites catalog file from www.celestrak.com

    Usage: 
    scfile = download_satcat()
    
    Outputs: 
    scfile -> [str] Path of satcat file
    '''
    home = str(Path.home())
    direc = home + '/src/satcat-data/'
    
    scfile = direc + 'satcat.txt'
    url = 'https://celestrak.com/pub/satcat.txt'

    if not path.exists(direc): makedirs(direc)

    if not path.exists(scfile):
        print('Downloading the latest satellite catalog from celestrak',end=' ... ')
        urlretrieve(url, scfile)
        print('Finished')

    else:
        modified_time = datetime.fromtimestamp(path.getmtime(scfile))
        if datetime.now() > modified_time + timedelta(days=7):
            remove(scfile)
            print('Updating the satellite catalog from celestrak',end=' ... ')
            urlretrieve(url, scfile)    
            print('Finished')
        else:
            print('The satellite catalog in {:s} is already the latest.'.format(direc))    
    return scfile

def celestrak_query(COSPARID = None, NORADID = None, Payload = None,Decayed = None,DecayDate = None,OrbitalPeriod = None,Inclination = None,ApoAlt = None,PerAlt = None,MeanAlt = None,Country = None,sort = None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the SATCAT Data from celestrak.

    Usage:
    df = celestrak_query(Payload = False,Decayed = False,MeanAlt = [400,900])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target ID by the in Committee On SPAce Research; If None, then this option is ignored.
    NORADID -> [int, str, list of int, or list of str, optional, default = None] Target ID by the North American Aerospace Defense Command; If None, then this option is ignored.
    Payload -> [bool, optional, fafault = None] If True, then targets belong to payload; if False, then non-payload; if None, then this option is ignored.
    Decayed ->  [bool, optional, default = None], also called reentry; If False, targets are still in orbit; if True, then reentry; if None, then this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    OrbitalPeriod -> [list of float with 2 elemnts, optional, default = None] orbit period[minutes] of targets; must be in form of [period1,period2], such as [100.0,200.0]; if None, then this option is ignored.  
    Inclination -> [list of float with 2 elemnts, optional, default = None] orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, then this option is ignored.  
    ApoAlt -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, then this option is ignored.  
    PerAlt -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, then this option is ignored.  
    MeanAlt -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then this option is ignored.  
    Country -> [str or list of str, optional, default = None] Satellite Ownership; if None, then this option is ignored.
    sort -> [str, optional, default = None] way of sorting, such as sort by MeanAlt; if None, then sort by NORADID defautly.
    outfile -> [bool, optional, default = True] If True, then a csv-formatted file named 'celestrak_catalog' is created; if False, then no files are generated.
    
    Outputs:
    df -> pandas dataframe
    celestrak_catalog.csv -> [optional] a csv-formatted file that records the pandas dataframe
    '''
    # Set the field width according to SATCAT Format Documentation[https://celestrak.com/satcat/satcat-format.php]
    set_colspecs = [(0,11),(13,18),(19,20),(20,21),(21,22),(23,47),(49,54),(56,66),(68,73),\
                    (75,85),(87,94),(96,101),(103,109),(111,117),(119,127),(129,132)]
    satcat_file = download_satcat()
    data = pd.read_fwf(satcat_file, colspecs = set_colspecs, header = None) 

    data.columns = ['COSPARID', 'NORADID', 'Multiple Name Flag', 'Payload Flag','Operational Status Code','Satellite Name',\
                    'Country','Launch Date','Launch Site','Decay Date','Orbital period[min]','Inclination[deg]',\
                    'Apogee Altitude[km]','Perigee Altitude[km]','Radar Cross Section[m2]','Orbital Status Code']

    Mean_Alltitude = (data['Apogee Altitude[km]'] + data['Perigee Altitude[km]'])/2 # mean alltitude[kilometers]
    full_of_true = np.ones_like(Mean_Alltitude,dtype=bool)
    
    # Filter parameters for 'COSPARID' 
    if COSPARID is not None:
        if type(COSPARID) in [str,list]:
            COSPARID_flag = np.in1d(data['COSPARID'],COSPARID,assume_unique=True)
        else:
            raise Exception('Type of COSPARID should be in str or list of str.')             
    else:
        COSPARID_flag = full_of_true
    
    # Filter parameters for 'NORADID' 
    if NORADID is not None:
        if type(NORADID) is int:
            NORADID_flag = np.in1d(data['NORADID'],NORADID,assume_unique=True)
        elif type(NORADID) is str:   
            NORADID_flag = np.in1d(data['NORADID'],int(NORADID),assume_unique=True)
        elif type(NORADID) is list:
            NORADID_flag = np.in1d(data['NORADID'],np.array(NORADID).astype(int),assume_unique=True)
        else:
            raise Exception('Type of NORADID should be in int, str, list of int, or list of str.')             
    else:
        NORADID_flag = full_of_true
    
    # Filter parameters for 'Payload'
    Payload_flag = data['Payload Flag'] == '*'
    if Payload is True:
        pass
    elif Payload is False:
        Payload_flag = ~Payload_flag
    else:
        Payload_flag = full_of_true
        
    # Filter parameters for 'Decayed' 
    Decayed_flag = data['Operational Status Code'] == 'D'
    if Decayed is True:
        pass
    elif Decayed is False:
        Decayed_flag = ~Decayed_flag
    else:
        Decayed_flag = full_of_true
       
    # Filter parameters for 'ApoAlt'
    if ApoAlt is not None:
        ApoAlt_flag = (data['Apogee Altitude[km]'] > ApoAlt[0]) & (data['Apogee Altitude[km]'] < ApoAlt[1])
    else:
        ApoAlt_flag = full_of_true
        
    # Filter parameters for 'PerAlt'
    if PerAlt is not None:
        PerAlt_flag = (data['Perigee Altitude[km]'] > PerAlt[0]) & (data['Perigee Altitude[km]'] < PerAlt[1])
    else:
        PerAlt_flag = full_of_true
        
    # Filter parameters for 'MeanAlt'
    if MeanAlt is not None:
        MeanAlt_flag = (Mean_Alltitude > MeanAlt[0]) & (Mean_Alltitude < MeanAlt[1])
    else:
        MeanAlt_flag = full_of_true    
       
    combined_flag = COSPARID_flag & NORADID_flag & Payload_flag & Decayed_flag & ApoAlt_flag & PerAlt_flag & MeanAlt_flag

    # Remove unwanted columns and readjust the order of the column    
    df = data[combined_flag].drop(['Multiple Name Flag','Operational Status Code','Orbital Status Code'],axis=1)
    column_reorder = ['COSPARID', 'NORADID', 'Satellite Name','Payload Flag','Decay Date',\
                      'Orbital period[min]', 'Inclination[deg]','Apogee Altitude[km]', 'Perigee Altitude[km]',\
                      'Launch Date','Launch Site','Radar Cross Section[m2]','Country']
    df = df.reindex(columns=column_reorder)
    if outfile: df.to_csv('celestrak_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df

def target_query(COSPARID=None,NORADID=None,Payload=None,ObjectClass=None,Mass=None,Decayed=None,DecayDate=None,OrbitalPeriod=None,Inclination=None,ApoAlt=None,PerAlt=None,MeanAlt=None,RCSMin=None,RCSMax=None,RCSAvg=None,Country=None,sort=None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the DISCOS and CELESTRAK database.

    Usage: 
    df = target_query(Payload = False,Decayed = False,MeanAlt = [400,900],RCSAvg=[5,15])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target ID by the in Committee On SPAce Research; If None, then this option is ignored. 
    NORADID -> [int, str, list of int, or list of str, optional, default = None] Target ID by the North American Aerospace Defense Command; If None, then this option is ignored.
    Payload -> [bool, optional, fafault = None] If True, then targets belong to payload; if False, then non-payload; if None, then this option is ignored.
    ObjectClass -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Ralated Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, then this option is ignored.  
    Mass -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; must be in form of [mass1,mass2], such as [5.0,10.0]; if None, then this option is ignored.
    Decayed ->  [bool, optional, default = None], also called reentry; If False, targets are still in orbit; if True, then reentry; if None, then this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    OrbitalPeriod -> [list of float with 2 elemnts, optional, default = None] orbit period[minutes] of targets; must be in form of [period1,period2], such as [100.0,200.0]; if None, then this option is ignored.  
    Inclination -> [list of float with 2 elemnts, optional, default = None] orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, then this option is ignored.  
    ApoAlt -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, then this option is ignored.  
    PerAlt -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, then this option is ignored.  
    MeanAlt -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then this option is ignored.  
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, then this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Mimimum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, then this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [5,20]; if None, then this option is ignored.
    Country -> [str or list of str, optional, default = None] Satellite Ownership; if None, then this option is ignored.
    sort -> [str, optional, default = None] way of sorting, such as sort by mass; if None, then sort by NORADID defautly.
    outfile -> [bool, optional, default = True] If True, then a csv-formatted file named 'discos_catalog' is created; if False, then no files are generated.
    
    Outputs:
    df -> pandas dataframe
    discos_catalog.csv -> [optional] a csv-formatted file that records the pandas dataframe
    '''
    df_celestrak = celestrak_query(COSPARID,NORADID,Payload,Decayed,DecayDate,OrbitalPeriod,Inclination,ApoAlt,PerAlt,MeanAlt,Country,outfile=False).drop('Satellite Name',axis=1)
    print('Go through the DISCOS database:')

    if Payload is True:
        ObjectClass = ['Payload','Payload Mission Related Object','Rocket Mission Related Object','Other Mission Related Object','Unknown']
    elif Payload is False:
    	ObjectClass = ['Payload Debris', 'Payload Fragmentation Debris','Rocket Body','Rocket Debris','Rocket Fragmentation Debris','Other Debris']
    else:
    	pass
           
    df_discos = discos_query(COSPARID,NORADID,ObjectClass,Decayed,DecayDate,Mass,RCSMin,RCSMax,RCSAvg,outfile=False).dropna(subset=['NORADID'])
    
    # Take the intersection of CELESTRAK and DISCOS
    nid,nid_celestrak,nid_discos = np.intersect1d(df_celestrak['NORADID'],df_discos['NORADID'],assume_unique=True,return_indices=True)
    df_celestrak = df_celestrak.iloc[nid_celestrak]
    df_discos = df_discos.iloc[nid_discos]
    
    # merge pandas dataframes
    df = pd.merge(df_celestrak, df_discos, on=['COSPARID','NORADID'],validate="one_to_one")
    # Remove unwanted columns and readjust the order of the column 
    df = df.drop(['Payload Flag','Radar Cross Section[m2]','VimpelId'],axis=1)
    column_reorder = ['COSPARID', 'NORADID', 'Satellite Name','ObjectClass','Mass[kg]','Shape',\
                      'Height[m]', 'Length[m]','Depth[m]','RCSMin[m2]', 'RCSMax[m2]', 'RCSAvg[m2]',\
                      'Orbital period[min]', 'Inclination[deg]','Apogee Altitude[km]', 'Perigee Altitude[km]',\
                      'Launch Date', 'Decay Date','Launch Site','Country']
    df = df.reindex(columns=column_reorder)
    if outfile: df.to_csv('target_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df                