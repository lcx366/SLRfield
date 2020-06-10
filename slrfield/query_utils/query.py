import numpy as np
import pandas as pd
from os import path,makedirs,remove
from pathlib import Path
import requests
from urllib.request import urlretrieve
from datetime import datetime,timedelta

def discos_buildin_filter(params,expr):
    '''
    A subfunction dedicated to the function discos_query. It is used for upgrading the variable params(type of dictionary) in discos_query based on
    params and expr. If key 'filter' does not exist in params, then the upgraded params will become params['filter'] = expr; otherwise, the upgraded params will become params['filter'] += '&(' + expr + ')'

    Usage:
    params_upgrade = discos_buildin_filter(params,expr)

    Inputs:
    params -> [dictionary] variable params in function discos_query
    expr -> [str] filter expressions for DISCOS, for example, "eq(reentry.epoch,null)". 
    For more infomation, please reference to https://discosweb.esoc.esa.int/apidocs

    Outputs:
    params_upgrade -> [dictionary] upgraded variable params in function discos_query
    '''
    if 'filter' in params.keys(): 
        params['filter'] += '&(' + expr + ')'
    else:
        params['filter'] = expr 
    return params  

def discos_query(COSPARID=None,NORADID=None,ObjectClass=None,Payload=None,Decayed=None,DecayDate=None,Mass=None,Shape=None,Length=None,Height=None,Depth=None,RCSMin=None,RCSMax=None,RCSAvg=None,sort=None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.

    Usage: 
    df = discos_query(Decayed=False,RCSAvg=[5,15])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored. 
    NORADID -> [int, str, list of int/str, optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    Note: if the NORADID list contains 2 elements, namely, in form of [noradid_i,noradid_j], then these two elements form an interval. 
    Furthermore, if the lower boundary of the interval is the same as the upper boundary, it is equivalent to setting a single value.
    ObjectClass -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.  
    Playload -> [bool, optional, default  = None] Identify whether a target belongs to payload or not. If True, payload; if False, non-payload; if None, this option is ignored.
    Decayed ->  [bool, optional, default = None] it also called reentry; If False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    Mass -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
    Shape -> [str or list of str, optional, default = None] Shape of targets; commonly used options include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
    'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combinations of them are also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
    Length -> [list of float with 2 elemnts, optional, default = None] Length[m] of a target; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
    Height -> [list of float with 2 elemnts, optional, default = None] Height[m] of a target; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
    Depth -> [list of float with 2 elemnts, optional, default = None] Depth[m] of a target; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Minimum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [5,20]; if None, this option is ignored.
    sort -> [str, optional, default = None] sort by features of targets in a specific order, such as by mass; avaliable options include 'COSPARID', NORADID', 'ObjectClass', 'DecayDate', 'Mass', 'Shape', 'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', and 'RCSAvg'.
    If there is a negative sign '-' ahead, such as "-Mass", it will be sorted in descending order. If None, then sort by NORADID by default.
    outfile -> [bool, optional, default = True] If True, then the file 'discos_catalog.csv' is created; if False, no files are generated.
    
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
        outfile_token = open(tokenfile,'w')
        outfile_token.write(token)
        outfile_token.close()
    else:
        infile = open(tokenfile,'r')
        token = infile.readline()
        infile.close()
    
    URL = 'https://discosweb.esoc.esa.int'
    params = {}
    
    # Filter parameters for 'ObjectClass' 
    if ObjectClass is not None:
        if type(ObjectClass) is str:
            params['filter'] = "eq(objectClass,'{:s}')".format(ObjectClass)
        elif type(ObjectClass) is list:
            params_filter = []
            for element in ObjectClass:
                params_filter.append("eq(objectClass,'{:s}')".format(element))
            params['filter'] = '(' + '|'.join(params_filter) + ')'
        else:
            raise Exception('Type of ObjectClass should be either string or list.')  

    # Set Payload based on ObjectClass
    if Payload is not None:
        if Payload is True:
            PayloadtoObjectClass = ['Payload','Payload Mission Related Object','Rocket Mission Related Object','Other Mission Related Object','Unknown']
        elif Payload is False:
            PayloadtoObjectClass = ['Payload Debris', 'Payload Fragmentation Debris','Rocket Body','Rocket Debris','Rocket Fragmentation Debris','Other Debris']
        else:
            raise Exception('Type of Payload should be either None, True or False.')  

        params_filter = []
        for element in PayloadtoObjectClass:
            params_filter.append("eq(objectClass,'{:s}')".format(element))
            temp = '(' + '|'.join(params_filter) + ')'
        params = discos_buildin_filter(params,temp)    

    # Set Decayed based on reentry.epoch 
    if Decayed is not None:
        if Decayed is False:
            temp = "eq(reentry.epoch,null)"
        elif Decayed is True:
            temp = "ne(reentry.epoch,null)"
        else:
            raise Exception("'Decayed' must be one of 'False', 'True', or 'None'.")  
        params = discos_buildin_filter(params,temp)     

    # Filter parameters for 'DecayDate'
    if DecayDate is not None:
        temp = "ge(reentry.epoch,epoch:'{:s}')&le(reentry.epoch,epoch:'{:s}')".format(DecayDate[0],DecayDate[1])
        params = discos_buildin_filter(params,temp)
    
    # Filter parameters for 'COSPARID'
    if COSPARID is not None:
        if type(COSPARID) is str:
            temp = "eq(cosparId,'{:s}')".format(COSPARID)
        elif type(COSPARID) is list:    
            temp = 'in(cosparId,{:s})'.format(str(tuple(COSPARID))).replace(' ', '')
        else:
            raise Exception('Type of COSPARID should be in str or list of str.')
        params = discos_buildin_filter(params,temp)    
            
    # Filter parameters for 'NORADID'        
    if NORADID is not None:
        if type(NORADID) is int or type(NORADID) is str:
            temp = 'eq(satno,{:s})'.format(str(NORADID))   
        elif type(NORADID) is list: 
            if len(NORADID) == 2:
                temp = 'ge(satno,{:d})&le(satno,{:d})'.format(int(NORADID[0]),int(NORADID[1]))
            else:   
                temp = 'in(satno,{:s})'.format(str(tuple(NORADID))).replace(' ', '')         
        else:
            raise Exception('Type of NORADID should be in int, str, list of int, or list of str.') 
        params = discos_buildin_filter(params,temp)    
            
    # Filter parameters for 'Mass'            
    if Mass is not None:
        temp = 'ge(mass,{:.2f})&le(mass,{:.2f})'.format(Mass[0],Mass[1])
        params = discos_buildin_filter(params,temp)

    # Filter parameters for 'Shape' 
    if Shape is not None:
        if type(Shape) is str:
            temp = "icontains(shape,'{:s}')".format(Shape)
        elif type(Shape) is list:
            shape_filter = []
            end_symbol = Shape[-1]
            if end_symbol == '+':
                for element in Shape[:-1]:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '&'.join(shape_filter)
            else:
                for element in Shape:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '|'.join(shape_filter)
        else:
            raise Exception('Type of Shape should either be string or list.')
        params = discos_buildin_filter(params,temp)   

    # Filter parameters for 'Length'            
    if Length is not None:
        temp = 'ge(length,{:.2f})&le(length,{:.2f})'.format(Length[0],Length[1])
        params = discos_buildin_filter(params,temp)  
            
    # Filter parameters for 'Height'            
    if Height is not None:
        temp = 'ge(height,{:.2f})&le(height,{:.2f})'.format(Height[0],Height[1])
        params = discos_buildin_filter(params,temp)
            
    # Filter parameters for 'Depth'            
    if Depth is not None:
        temp = 'ge(depth,{:.2f})&le(depth,{:.2f})'.format(Depth[0],Depth[1])   
        params = discos_buildin_filter(params,temp)                     

    # Filter parameters for 'RCSMin'            
    if RCSMin is not None:
        temp = 'ge(xSectMin,{:.4f})&le(xSectMin,{:.4f})'.format(RCSMin[0],RCSMin[1])
        params = discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSMax'     
    if RCSMax is not None:
        temp = 'ge(xSectMax,{:.4f})&le(xSectMax,{:.4f})'.format(RCSMax[0],RCSMax[1])
        params = discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSAvg'     
    if RCSAvg is not None:
        temp = 'ge(xSectAvg,{:.4f})&le(xSectAvg,{:.4f})'.format(RCSAvg[0],RCSAvg[1])
        params = discos_buildin_filter(params,temp)
    
    # Sort in ascending order       
    if sort is None:    
        params['sort'] = 'satno'  
    else:
        if sort.__contains__('COSPARID'):
            params['sort'] = 'cosparId'
        elif sort.__contains__('NORADID'):
            params['sort'] = 'satno'    
        elif sort.__contains__('ObjectClass'):
            params['sort'] = 'objectClass'  
        elif sort.__contains__('Mass'):
            params['sort'] = 'mass'    
        elif sort.__contains__('Shape'):
            params['sort'] = 'shape'
        elif sort.__contains__('Length'):
            params['sort'] = 'length'   
        elif sort.__contains__('Height'):
            params['sort'] = 'height'
        elif sort.__contains__('Depth'):
            params['sort'] = 'depth'
        elif sort.__contains__('RCSMin'):
            params['sort'] = 'xSectMin'
        elif sort.__contains__('RSCMax'):
            params['sort'] = 'xSectMax' 
        elif sort.__contains__('RCSAvg'):
            params['sort'] = 'xSectAvg'  
        elif sort.__contains__('DecayDate'):
            params['sort'] = 'reentry.epoch'
        else:
            raise Exception("Avaliable options include 'COSPARID', NORADID', 'ObjectClass', 'Mass', 'Shape', 'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', 'RCSAvg', and 'DecayDate'. Also, a negative sign '-' can be added to the option to sort in descending order.")        
                
        # Sort in descending order
        if sort[0] == '-': params['sort'] = '-' + params['sort']

    # Initialize the page parameter 
    params['page[number]'] = 1
    extract = []
    
    while True:
        params['page[size]'] = 100 # Number of entries on each page   
        response = requests.get(f'{URL}/api/objects',headers = {'Authorization': f'Bearer {token}'},params = params)
        doc = response.json()

        if response.ok:
            if not doc['data']: raise Exception('No entries found that meet the conditions, please reset the filter parameters.')
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
    
    # Rename the columns and readjust the order of the columns  
    old_column = ['height', 'xSectMax', 'name', 'satno', 'vimpelId', 'objectClass','mass', 'xSectMin', 'depth', 'xSectAvg', 'length', 'shape', 'cosparId']
    new_column = ['Height[m]', 'RCSMax[m2]', 'Satellite Name', 'NORADID', 'VimpelId', 'ObjectClass', 'Mass[kg]', 'RCSMin[m2]', 'Depth[m]', 'RCSAvg[m2]', 'Length[m]', 'Shape', 'COSPARID']
    new_column_reorder = ['COSPARID', 'NORADID', 'VimpelId', 'Satellite Name','ObjectClass','Mass[kg]','Shape','Height[m]','Length[m]','Depth[m]','RCSMin[m2]','RCSMax[m2]','RCSAvg[m2]']
    df = pd.DataFrame.from_dict(extract,dtype=object).rename(columns=dict(zip(old_column, new_column)), errors='raise')
    df = df.reindex(columns=new_column_reorder) 
    df = df.reset_index(drop=True)
    if outfile: df.to_csv('discos_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df   

def download_satcat():
    '''
    Download or update the satellites catalog file from www.celestrak.com

    Usage: 
    scfile = download_satcat()
    
    Outputs: 
    scfile -> [str] Local path of the satellites catalog file
    '''
    home = str(Path.home())
    direc = home + '/src/satcat-data/'
    
    scfile = direc + 'satcat.txt'
    url = 'https://celestrak.com/pub/satcat.txt'

    if not path.exists(direc): makedirs(direc)

    if not path.exists(scfile):
        print('Downloading the latest satellite catalog from CELESTRAK',end=' ... ')
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

def celestrak_query(COSPARID=None,NORADID=None,Payload=None,Decayed=None,DecayDate=None,OrbitalPeriod=None,Inclination=None,ApoAlt=None,PerAlt=None,MeanAlt=None,Country=None,sort=None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the [CELESTRAK](https://celestrak.com) database.

    Usage:
    df = celestrak_query(Payload = False,Decayed = False,MeanAlt = [400,900])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored.
    NORADID -> [int, str, list of int/str, optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    Note: if the NORADID list contains 2 elements, namely, in form of [noradid_i,noradid_j], then these two elements form an interval. 
    Furthermore, if the lower boundary of the interval is the same as the upper boundary, it is equivalent to setting a single value.
    Playload -> [bool, optional, default  = None] Identify whether a target belongs to payload or not. If True, payload; if False, non-payload; if None, this option is ignored.
    Decayed ->  [bool, optional, default = None] It also called reentry; if False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, this option is ignored.
    OrbitalPeriod -> [list of float with 2 elemnts, optional, default = None] Orbit period[minutes] of targets; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
    Inclination -> [list of float with 2 elemnts, optional, default = None] Orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
    ApoAlt -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
    PerAlt -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
    MeanAlt -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored.  
    Country -> [str or list of str, optional, default = None] Satellite Ownership; country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
    sort -> [str, optional, default = None] sort by features of targets in a specific order, such as by mass; avaliable options include 'COSPARID', NORADID', 'DecayDate', 'OrbitalPeriod', 'Inclination', 'ApoAlt', 'PerAlt', 'MeanAlt', and 'Country'.
    If there is a negative sign '-' ahead, such as "-DecayDate", it will be sorted in descending order. If None, then sort by NORADID by default.
    outfile -> [bool, optional, default = True] If True, then the file 'celestrak_catalog.csv' is created; if False, no files are generated.
    
    Outputs:
    df -> pandas dataframe
    celestrak_catalog.csv -> [optional] a csv-formatted file that records the pandas dataframe
    '''
    # Set the field width according to the SATCAT Format Documentation[https://celestrak.com/satcat/satcat-format.php]
    set_colspecs = [(0,11),(13,18),(19,20),(20,21),(21,22),(23,47),(49,54),(56,66),(68,73),\
                    (75,85),(87,94),(96,101),(103,109),(111,117),(119,127),(129,132)]
    satcat_file = download_satcat()
    data = pd.read_fwf(satcat_file, colspecs = set_colspecs, header = None) 

    data.columns = ['COSPARID', 'NORADID', 'Multiple Name Flag', 'Payload Flag','Operational Status Code','Satellite Name',\
                    'Country','Launch Date','Launch Site','Decay Date','Orbital Period[min]','Inclination[deg]',\
                    'Apogee Altitude[km]','Perigee Altitude[km]','Radar Cross Section[m2]','Orbital Status Code']

    Mean_Alltitude = (data['Apogee Altitude[km]'] + data['Perigee Altitude[km]'])/2 # Compute the mean alltitude

    # Add column to dataframe
    data['Mean Altitude[km]'] = Mean_Alltitude
    full_of_true = np.ones_like(Mean_Alltitude,dtype=bool)
    
    # Set filter for 'COSPARID' 
    if COSPARID is not None:
        if type(COSPARID) in [str,list]:
            COSPARID_flag = np.in1d(data['COSPARID'],COSPARID,assume_unique=True)
        else:
            raise Exception('Type of COSPARID should be in str or list of str.')             
    else:
        COSPARID_flag = full_of_true
    
    # Set filter for 'NORADID' 
    if NORADID is not None:
        if type(NORADID) is int:
            NORADID_flag = np.in1d(data['NORADID'],NORADID,assume_unique=True)
        elif type(NORADID) is str:   
            NORADID_flag = np.in1d(data['NORADID'],int(NORADID),assume_unique=True)
        elif type(NORADID) is list:
            if len(NORADID) == 2:
                NORADID_list = np.arange(int(NORADID[0]),int(NORADID[1])+1)
            else:
                NORADID_list = np.array(NORADID).astype(int)       
            NORADID_flag = np.in1d(data['NORADID'],NORADID_list,assume_unique=True)        
        else:
            raise Exception('Type of NORADID should be in int, str, list of int, or list of str.')             
    else:
        NORADID_flag = full_of_true   
    
    # Set filter for 'Payload'
    Payload_flag = data['Payload Flag'] == '*'
    if Payload is True:
        pass
    elif Payload is False:
        Payload_flag = ~Payload_flag
    else:
        Payload_flag = full_of_true
        
    # Set filter for 'Decayed' 
    Decayed_flag = data['Operational Status Code'] == 'D'
    if Decayed is True:
        pass
    elif Decayed is False:
        Decayed_flag = ~Decayed_flag
    else:
        Decayed_flag = full_of_true

    # Set filter for 'DecayDate'
    if DecayDate is not None:
        DecayDate_flag = (data['Decay Date'] > DecayDate[0]) & (data['Decay Date'] < DecayDate[1])
    else:
        DecayDate_flag = full_of_true

    # Set filter for 'OrbitalPeriod'
    if OrbitalPeriod is not None:
        OrbitalPeriod_flag = (data['Orbital Period[min]'] > OrbitalPeriod[0]) & (data['Orbital Period[min]'] < OrbitalPeriod[1])
    else:
        OrbitalPeriod_flag = full_of_true   

    # Set filter for 'Inclination'
    if Inclination is not None:
        Inclination_flag = (data['Inclination[deg]'] > Inclination[0]) & (data['Inclination[deg]'] < Inclination[1])
    else:
        Inclination_flag = full_of_true
       
    # Set filter for 'ApoAlt'
    if ApoAlt is not None:
        ApoAlt_flag = (data['Apogee Altitude[km]'] > ApoAlt[0]) & (data['Apogee Altitude[km]'] < ApoAlt[1])
    else:
        ApoAlt_flag = full_of_true
        
    # Set filter for 'PerAlt'
    if PerAlt is not None:
        PerAlt_flag = (data['Perigee Altitude[km]'] > PerAlt[0]) & (data['Perigee Altitude[km]'] < PerAlt[1])
    else:
        PerAlt_flag = full_of_true
        
    # Set filter for 'MeanAlt'
    if MeanAlt is not None:
        MeanAlt_flag = (Mean_Alltitude > MeanAlt[0]) & (Mean_Alltitude < MeanAlt[1])
    else:
        MeanAlt_flag = full_of_true    

    # Set filter for 'Country'
    if Country is not None:
        if type(Country) in [str,list]:
            Country_flag = np.in1d(data['Country'],Country)
        else:
            raise Exception('Type of Country should be in str or list of str.') 
    else:
        Country_flag = full_of_true    

    # Combine filters
    combined_flag = COSPARID_flag & NORADID_flag & Payload_flag & Decayed_flag & DecayDate_flag & OrbitalPeriod_flag & Inclination_flag & ApoAlt_flag & PerAlt_flag & MeanAlt_flag & Country_flag
    df = data[combined_flag]

    # Eeadjust the order of the columns 
    column_reorder = ['COSPARID', 'NORADID', 'Satellite Name','Multiple Name Flag','Payload Flag','Operational Status Code','Decay Date',\
                      'Orbital Period[min]', 'Inclination[deg]','Apogee Altitude[km]','Perigee Altitude[km]','Mean Altitude[km]',\
                      'Launch Date','Launch Site','Radar Cross Section[m2]','Country','Orbital Status Code']
    df = df.reindex(columns=column_reorder)
            
    # Sort     
    if sort is None:    
        df = df.sort_values(by=['NORADID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
    
        if sort.__contains__('COSPARID'):
            df = df.sort_values(by=['COSPARID'],ascending=ascending_flag)
        elif sort.__contains__('NORADID'):
            df = df.sort_values(by=['NORADID'],ascending=ascending_flag)   
        elif sort.__contains__('DecayDate'):
            df = df.sort_values(by=['Decay Date'],ascending=ascending_flag)   
        elif sort.__contains__('OrbitalPeriod'):
            df = df.sort_values(by=['Orbital Period[min]'],ascending=ascending_flag)    
        elif sort.__contains__('Inclination'):
            df = df.sort_values(by=['Inclination[deg]'],ascending=ascending_flag) 
        elif sort.__contains__('ApoAlt'):
            df = df.sort_values(by=['Apogee Altitude[km]'],ascending=ascending_flag)   
        elif sort.__contains__('PerAlt'):
            df = df.sort_values(by=['Perigee Altitude[km]'],ascending=ascending_flag) 
        elif sort.__contains__('MeanAlt'):
            df = df.sort_values(by=['Mean Altitude[km]'],ascending=ascending_flag) 
        elif sort.__contains__('LaunchDate'):
            df = df.sort_values(by=['Launch Date'],ascending=ascending_flag) 
        elif sort.__contains__('LaunchSite'):
            df = df.sort_values(by=['Launch Site'],ascending=ascending_flag)     
        elif sort.__contains__('RCS'):
            df = df.sort_values(by=['Radar Cross Section[m2]'],ascending=ascending_flag)    
        elif sort.__contains__('Country'):
            df = df.sort_values(by=['Country'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPARID', NORADID', 'DecayDate', 'OrbitalPeriod', 'Inclination', 'ApoAlt', 'PerAlt', 'MeanAlt', 'LaunchDate', 'LaunchSite', 'RCS', and 'Country'. Also, a negative sign '-' can be added ahead to the option to sort in descending order.")
    df = df.reset_index(drop=True)
    if outfile: df.to_csv('celestrak_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df

def target_query(COSPARID=None,NORADID=None,Payload=None,ObjectClass=None,Mass=None,Shape=None,Decayed=None,DecayDate=None,OrbitalPeriod=None,Inclination=None,ApoAlt=None,PerAlt=None,MeanAlt=None,Length=None,Height=None,Depth=None,RCSMin=None,RCSMax=None,RCSAvg=None,Country=None,sort=None,outfile=True):
    '''
    Query space targets that meet the requirements by setting a series of specific parameters from the the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.

    Usage: 
    df = target_query(Payload = False,Decayed = False,MeanAlt = [400,900],RCSAvg=[5,15])

    Parameters:
    COSPARID -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored.
    NORADID -> [int, str, list of int/str, optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    Note: if the NORADID list contains 2 elements, namely, in form of [noradid_i,noradid_j], then these two elements form an interval. 
    Furthermore, if the lower boundary of the interval is the same as the upper boundary, it is equivalent to setting a single value.
    Payload -> [bool, optional, fafault = None] Identify whether a target belongs to payload or not. If True, then targets belong to payload; if False, then non-payload; if None, then this option is ignored.
    ObjectClass -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.
    Mass -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
    Decayed ->  [bool, optional, default = None] it also called reentry; If False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DecayDate -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    OrbitalPeriod -> [list of float with 2 elemnts, optional, default = None] Orbit period[minutes] of targets; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
    Inclination -> [list of float with 2 elemnts, optional, default = None] Orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
    ApoAlt -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
    PerAlt -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
    MeanAlt -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored.  
    Length -> [list of float with 2 elemnts, optional, default = None] Length[m] of a target; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
    Height -> [list of float with 2 elemnts, optional, default = None] Height[m] of a target; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
    Depth -> [list of float with 2 elemnts, optional, default = None] Depth[m] of a target; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, then this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Mimimum Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, then this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; must be in form of [RCS1,RCS2], such as [5,20]; if None, then this option is ignored.
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Minimum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [5,20]; if None, this option is ignored.
    Country -> [str or list of str, optional, default = None] Satellite Ownership; country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
    sort -> [str, optional, default = None] sort by features of targets in a specific order, such as by mass; avaliable options include 'COSPARID', NORADID', 'ObjectClass', 'Mass', 'DecayDate', 'Shape', 
    'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', 'RCSAvg', 'OrbitalPeriod', 'Inclination', 'ApoAlt', 'PerAlt', 'MeanAlt', and 'Country'.
    If there is a negative sign '-' ahead, such as "-RCSAvg", it will be sorted in descending order. If None, then sort by NORADID by default.
    outfile -> [bool, optional, default = True] If True, then the file 'celestrak_catalog.csv' is created; if False, no files are generated.
    
    Outputs:
    df -> pandas dataframe
    discos_catalog.csv -> [optional] a csv-formatted file that records the pandas dataframe
    '''
    # Query space targets from the CELESTRAK database
    df_celestrak = celestrak_query(COSPARID,NORADID,Payload,Decayed,DecayDate,OrbitalPeriod,Inclination,ApoAlt,PerAlt,MeanAlt,Country,outfile=False).drop('Satellite Name',axis=1)
    
    # Query space targets from the DISCOS database
    print('Go through the DISCOS database:')    
    df_discos = discos_query(COSPARID,NORADID,ObjectClass,Payload,Decayed,DecayDate,Mass,Shape,Length,Height,Depth,RCSMin,RCSMax,RCSAvg,outfile=False).dropna(subset=['NORADID'])
    
    # Take the intersection of CELESTRAK and DISCOS
    nid,nid_celestrak,nid_discos = np.intersect1d(df_celestrak['NORADID'],df_discos['NORADID'],assume_unique=True,return_indices=True)
    df_celestrak = df_celestrak.iloc[nid_celestrak]
    df_discos = df_discos.iloc[nid_discos]
    
    # Merge pandas dataframes
    df = pd.merge(df_celestrak, df_discos, on=['COSPARID','NORADID'],validate="one_to_one")

    # Remove unwanted columns and readjust the order of the columns 
    df = df.drop(['Radar Cross Section[m2]','VimpelId'],axis=1)
    column_reorder = ['COSPARID', 'NORADID', 'Satellite Name','Multiple Name Flag','ObjectClass','Payload Flag','Operational Status Code','Mass[kg]','Shape',\
                      'Length[m]', 'Height[m]','Depth[m]','RCSMin[m2]', 'RCSMax[m2]', 'RCSAvg[m2]',\
                      'Orbital Period[min]', 'Inclination[deg]','Apogee Altitude[km]', 'Perigee Altitude[km]','Mean Altitude[km]',\
                      'Launch Date', 'Decay Date','Launch Site','Country','Orbital Status Code']
    df = df.reindex(columns=column_reorder)  
         
    # Sort
    if sort is None:    
        df = df.sort_values(by=['NORADID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
        
        if sort.__contains__('COSPARID'):
            df = df.sort_values(by=['COSPARID'],ascending=ascending_flag)
        elif sort.__contains__('NORADID'):
            df = df.sort_values(by=['NORADID'],ascending=ascending_flag)  
        elif sort.__contains__('ObjectClass'):
            df = df.sort_values(by=['ObjectClass'],ascending=ascending_flag)   
        elif sort.__contains__('Mass'):
            df = df.sort_values(by=['Mass[kg]'],ascending=ascending_flag) 
        elif sort.__contains__('Shape'):
            df = df.sort_values(by=['Shape'],ascending=ascending_flag)    
        elif sort.__contains__('Length'):
            df = df.sort_values(by=['Length[m]'],ascending=ascending_flag)
        elif sort.__contains__('Height'):
            df = df.sort_values(by=['Height[m]'],ascending=ascending_flag)
        elif sort.__contains__('Depth'):
            df = df.sort_values(by=['Depth[m]'],ascending=ascending_flag)   
        elif sort.__contains__('RCSMin'): 
            df =  df.sort_values(by=['RCSMin[m2]'],ascending=ascending_flag)  
        elif sort.__contains__('RCSMax'): 
            df =  df.sort_values(by=['RCSMax[m2]'],ascending=ascending_flag)    
        elif sort.__contains__('RCSAvg'): 
            df =  df.sort_values(by=['RCSAvg[m2]'],ascending=ascending_flag)       
        elif sort.__contains__('DecayDate'):
            df = df.sort_values(by=['Decay Date'],ascending=ascending_flag)   
        elif sort.__contains__('OrbitalPeriod'):
            df = df.sort_values(by=['Orbital Period[min]'],ascending=ascending_flag)    
        elif sort.__contains__('Inclination'):
            df = df.sort_values(by=['Inclination[deg]'],ascending=ascending_flag) 
        elif sort.__contains__('ApoAlt'):
            df = df.sort_values(by=['Apogee Altitude[km]'],ascending=ascending_flag)   
        elif sort.__contains__('PerAlt'):
            df = df.sort_values(by=['Perigee Altitude[km]'],ascending=ascending_flag) 
        elif sort.__contains__('MeanAlt'):
            df = df.sort_values(by=['Mean Altitude[km]'],ascending=ascending_flag) 
        elif sort.__contains__('LaunchDate'):
            df = df.sort_values(by=['Launch Date'],ascending=ascending_flag) 
        elif sort.__contains__('LaunchSite'):
            df = df.sort_values(by=['Radar Cross Section[m2]'],ascending=ascending_flag)    
        elif sort.__contains__('Country'):
            df = df.sort_values(by=['Country'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPARID', NORADID', 'DecayDate', 'OrbitalPeriod', 'Inclination', 'ApoAlt', 'PerAlt', 'MeanAlt', 'LaunchDate', 'LaunchSite', 'RCS', and 'Country'. Also, a negative sign '-' can be added to the option to sort in descending order.")
    df = df.reset_index(drop=True)
    if outfile: df.to_csv('target_catalog.csv') # Save the pandas dataframe to a csv-formatted file
    return df                