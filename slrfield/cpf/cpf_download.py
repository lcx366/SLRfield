from os import system,path,remove,makedirs
from pathlib import Path
from ftplib import FTP
import requests
from bs4 import BeautifulSoup
from astropy.time import Time

from ..utils.try_download import tqdm_ftp,tqdm_request

def download_bycurrent(source,satnames,append=False):
    '''
    Download the latest CPF ephemeris files at the current moment.

    Usage: 
    server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('CDDIS')
    server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('EDC')
    server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('CDDIS',lageos1')
    server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('EDC',['ajisai','lageos1','hy2a'])

    Inputs:
    source -> [str] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    satnames -> [str, str list, or None] target name or list of target names. If None, then all feasible targets at the current moment will be downloaded.
    
    Parameters:
    append ->[Bool, default = False] If False, clear the data storage directory ahead of requesting CPF files. If True, then keep the data storage directory.

    Outputs:
    server -> [str] server for downloading CPF ephemeris files. Currently, only 'cddis.nasa.gov' and 'edc.dgfi.tum.de' are available.
    dir_cpf_from -> [str] directory for storing CPF ephemeris files in remote server.
    dir_cpf_to -> [str] user's local directory for storing CPF ephemeris files
    cpf_files -> [str list] list of CPF ephemeris files
    '''   
    cpf_files = []
    date = Time.now().iso
    dir_cpf_to = 'CPF/'+source+'/'+date[:10] + '/'
    
    if not path.exists(dir_cpf_to): 
        makedirs(dir_cpf_to)   
    else:
        if not append: system('rm -rf %s/*' % dir_cpf_to)
        
    if source == 'CDDIS':
        server = 'https://cddis.nasa.gov'
        dir_cpf_from = '/archive/slr/cpf_predicts/current/' 
        cpf_files_dict,cpf_files_list = get_cpf_filelist(server,dir_cpf_from,'bycurrent')
           
    elif source == 'EDC':
        server = 'edc.dgfi.tum.de'
        dir_cpf_from = '~/slr/cpf_predicts//current/'
        ftp = FTP(server,timeout=200)
        ftp.login()
        ftp.cwd(dir_cpf_from)
        cpf_files_list = ftp.nlst('-t','*cpf*') # list files containing 'cpf' from newest to oldest   
          
        ftp.quit()  
        ftp.close()
    else:    
        raise Exception("Currently, for CPF prediction centers, only 'CDDIS' and 'EDC' are available.")  

    if satnames is None:
        reduplicates = set([cpf_file.split('_')[0] for cpf_file in cpf_files_list]) # remove duplicates
    elif type(satnames) is str:
        reduplicates = [satnames]
    elif type(satnames) is list:
        reduplicates = satnames
    else:
        raise Exception('Type of satnames should be str or list.') 
        
    for cpf_file in cpf_files_list:
        satname = cpf_file.split('_')[0]
        if satname in reduplicates:
            cpf_files.append(cpf_file)
            reduplicates.remove(satname)
            if reduplicates == []: break       
      
    return server,dir_cpf_from, dir_cpf_to,cpf_files                   

def download_bydate(source,date,satnames,append=False): 
    '''
    Download the latest CPF ephemeris files before a specific time.

    Usage: 
    server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bydate('CDDIS','2007-06-01 11:30:00',['ajisai','lageos1','hy2a'])
    server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('EDC','2017-12-20 05:30:00','hy2a'])

    Inputs:
    source -> [str] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    date -> [str] 'iso-formatted' time, such as '2017-12-20 05:30:00'. It specifies a moment before which the latest CPF ephemeris files are downloaded.
    satnames -> [str, str list] target name or list of target names. 
    
    Parameters:
    append ->[Bool, default = False] If False, clear the data storage directory ahead of requesting CPF files. If True, then keep the data storage directory.

    Outputs:
    server -> [str] server for downloading CPF ephemeris files. Currently, only 'cddis.nasa.gov' and 'edc.dgfi.tum.de' are available.
    dir_cpf_from -> [str] directory for storing CPF ephemeris files in remote server.
    dir_cpf_to -> [str] user's local directory for storing CPF ephemeris files
    cpf_files -> [str list] list of CPF ephemeris files
    '''  
        
    if satnames is None:
        raise Exception("satnames must be provided.")      
    elif type(satnames) is str:
        reduplicates = [satnames]
    elif type(satnames) is list:
        reduplicates = satnames
    else:
        raise Exception('Type of satname should be str or list.')     
    
    dirs_cpf_from,cpf_files = [],[]
    date_dir = date[:4]
    date_str1  = Time(date).strftime('%y%m%d')
    date_str2  = (Time(date)-7).strftime('%y%m%d') # ephemeris updates for some high-orbit satellites may take several days
    date_str = Time(date).strftime('%Y%m%d%H%M%S')
    dir_cpf_to = 'CPF/'+source+'/'+ date[:10] + '/'
    
    if not path.exists(dir_cpf_to): 
        makedirs(dir_cpf_to)   
    else:
        if not append: system('rm -rf %s/*' % dir_cpf_to)
        
    if source == 'CDDIS':
        server = 'https://cddis.nasa.gov'   

        for satname in reduplicates:
            cpf_files_list_reduced = []
            find_flag = False
            dir_cpf_from = '/archive/slr/cpf_predicts/' + date_dir + '/' + satname + '/'
            dirs_cpf_from.append(dir_cpf_from)
            cpf_files_dict,cpf_files_list = get_cpf_filelist(server,dir_cpf_from,'bydate') 

            for cpf_file in cpf_files_list:
                cpf_file_date = cpf_file.split('_')[2]
                if date_str2 <= cpf_file_date <= date_str1: cpf_files_list_reduced.append(cpf_file)   
                    
            if cpf_files_list_reduced:
                for cpf_file in cpf_files_list_reduced:
                    # get the latest modification time for cpf files
                    modified_time = cpf_files_dict[cpf_file]
                    # modify the time format from '2020:09:20 05:30:11' to '20200920053011'
                    for chara in [':',' ']:
                        modified_time = modified_time.replace(chara,'') 

                    if modified_time < date_str: 
                        find_flag = True
                        cpf_files.append(cpf_file)  
                        break     

            if not find_flag and date_str2[:2]>='05':  
                cpf_files_list_reduced = []
                dirs_cpf_from.remove(dir_cpf_from)
                dir_cpf_from = '/archive/slr/cpf_predicts/' + '20'+date_str2[:2] + '/' + satname + '/'
                dirs_cpf_from.append(dir_cpf_from)
                cpf_files_dict,cpf_files_list = get_cpf_filelist(server,dir_cpf_from,'bydate')
    
                for cpf_file in cpf_files_list:
                    cpf_file_date = cpf_file.split('_')[2]
                    if date_str2 <= cpf_file_date <= date_str1: cpf_files_list_reduced.append(cpf_file)    
                        
                for cpf_file in cpf_files_list_reduced:
                    # get the latest modification time for cpf files
                    modified_time = cpf_files_dict[cpf_file]
                    # modify the time format from '2020:09:20 05:30:11' to '20200920053011'
                    for chara in [':',' ']:
                        modified_time = modified_time.replace(chara,'') 

                    if modified_time <= date_str: 
                        cpf_files.append(cpf_file)
                        break                

    elif source == 'EDC':
        server = 'edc.dgfi.tum.de'    
        ftp = FTP(server,timeout=200)    
        ftp.login()    

        for satname in reduplicates:
            cpf_files_list_reduced = []
            find_flag = False
            dir_cpf_from = '~/slr/cpf_predicts//' + date_dir + '/' + satname + '/'
            dirs_cpf_from.append(dir_cpf_from)
            ftp.cwd(dir_cpf_from)
            cpf_files_list = ftp.nlst('-t','*cpf*') # list files containing 'cpf' from newest to oldest  
            
            for cpf_file in cpf_files_list:
                cpf_file_date = cpf_file.split('_')[2]
                if date_str2 <= cpf_file_date <= date_str1: cpf_files_list_reduced.append(cpf_file)   
                    
            if cpf_files_list_reduced:
                for cpf_file in cpf_files_list_reduced:
                    # get the latest modification time for cpf files
                    modified_time = ftp.voidcmd('MDTM ' + cpf_file).split()[1]
                    if modified_time < date_str: 
                        find_flag = True
                        cpf_files.append(cpf_file)  
                        break       
                    
            if not find_flag and date_str2[:2]>='05':  
                cpf_files_list_reduced = []
                dirs_cpf_from.remove(dir_cpf_from)
                dir_cpf_from = '~/slr/cpf_predicts//' + '20'+date_str2[:2] + '/' + satname + '/'
                dirs_cpf_from.append(dir_cpf_from)
                ftp.cwd(dir_cpf_from)
                cpf_files_list = ftp.nlst('-t','*cpf*') # list files containing 'cpf' from newest to oldest 
                    
                for cpf_file in cpf_files_list:
                    cpf_file_date = cpf_file.split('_')[2]
                    if date_str2 <= cpf_file_date <= date_str1: cpf_files_list_reduced.append(cpf_file)    
                        
                for cpf_file in cpf_files_list_reduced:
                    # get the latest modification time for cpf files
                    modified_time = ftp.voidcmd('MDTM ' + cpf_file).split()[1]
                    if modified_time <= date_str: 
                        cpf_files.append(cpf_file)
                        break  
        ftp.quit()  
        ftp.close() 
                         
    else:    
        raise Exception("Currently, CPF predictions only from 'CDDIS' and 'EDC' are available.")     
            
    return server,dirs_cpf_from, dir_cpf_to,cpf_files

def cpf_download_prior(satnames = None,date = None,source = 'CDDIS',append=False):
    '''
    Download the latest CPF ephemeris files.

    Usage: 
    dir_cpf_files = cpf_download()
    dir_cpf_files = cpf_download(source = 'EDC')
    dir_cpf_files = cpf_download('lageos1')
    dir_cpf_files = cpf_download('ajisai','2007-06-01 11:30:00')
    dir_cpf_files = cpf_download(['ajisai','lageos1','hy2a'],'2007-06-01 11:30:00','EDC')

    Parameters:
    satnames -> [str, str list, or None, default = None] target name or list of target names. If None, then all feasible targets at the current moment will be downloaded. In this case, 'date' must also be None. 
    date -> [str or None, default = None] 'iso-formatted' time, such as '2017-12-20 05:30:00'. It specifies a moment before which the latest CPF ephemeris files are downloaded. If None, then all feasible targets or targets in list at the current moment will be downloaded.
    source -> [str, default = 'CDDIS'] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    append ->[Bool, default = False] If False, clear the data storage directory ahead of requesting CPF files. If True, then keep the data storage directory.
    
    Outputs:
    dir_cpf_files -> [str list] list of paths for CPF ephemeris files in user's local directory
    missing_cpf_files -> [str list or None] if None, it lists files that are not responsed from the server

    Note: if 'date' is provided, namely not None, then 'satnames' must also be provided.
    '''

    if source == 'CDDIS': # Need to create an Earthdata login account at https://urs.earthdata.nasa.gov/ 
        # Create a .netrc file in the home directory
        home = str(Path.home())
        if not path.exists(home+'/.netrc'):
            uid = input('Please input the Username for your EARTHDATA login account(which can be created at https://urs.earthdata.nasa.gov/): ')
            passwd = input('Please input the Password: ')
            netrc_file = open(home+'/.netrc','w')
            netrc_file.write('machine urs.earthdata.nasa.gov login '+uid+' password '+passwd)
            netrc_file.close()

    dir_cpf_files,missing_cpf_files = [],[]
    
    if date is None:
        server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent(source,satnames,append)  

        if source == 'CDDIS':
            for cpf_file in cpf_files:
                url = server+dir_cpf_from+cpf_file
                missing_cpf_file = tqdm_request(url,dir_cpf_to,cpf_file)
                if missing_cpf_file is not None: missing_cpf_files.append(missing_cpf_file)
                dir_cpf_files.append(dir_cpf_to+cpf_file)
                

        if source == 'EDC':
            ftp = FTP(server,timeout=200)    
            ftp.login()  
            ftp.cwd(dir_cpf_from) 
            for cpf_file in cpf_files:
                missing_cpf_file = tqdm_ftp(ftp,dir_cpf_to,cpf_file)
                if missing_cpf_file is not None: missing_cpf_files.append(missing_cpf_file)
                dir_cpf_files.append(dir_cpf_to+cpf_file)

            ftp.quit()  
            ftp.close()    
                
    else:    
        server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bydate(source,date,satnames,append)  

        if source == 'CDDIS':
            for dir_cpf_from,cpf_file in zip(dirs_cpf_from,cpf_files):
                url = server+dir_cpf_from+cpf_file
                missing_cpf_file = tqdm_request(url,dir_cpf_to,cpf_file)
                if missing_cpf_file is not None: missing_cpf_files.append(missing_cpf_file)
                dir_cpf_files.append(dir_cpf_to+cpf_file)

        if source == 'EDC': 
            ftp = FTP(server,timeout=200)    
            ftp.login()  

            for dir_cpf_from,cpf_file in zip(dirs_cpf_from,cpf_files):
                ftp.cwd(dir_cpf_from)
                missing_cpf_file = tqdm_ftp(ftp,dir_cpf_to,cpf_file)
                if missing_cpf_file is not None: missing_cpf_files.append(missing_cpf_file)
                dir_cpf_files.append(dir_cpf_to+cpf_file)

            ftp.quit()  
            ftp.close()    
                           

    return dir_cpf_files,missing_cpf_files
    
    
def cpf_download(satnames = None,date = None,source = 'CDDIS',append=False):
    '''
    Download the latest CPF ephemeris files.

    Usage: 
    dir_cpf_files = cpf_download()
    dir_cpf_files = cpf_download(source = 'EDC')
    dir_cpf_files = cpf_download('lageos1')
    dir_cpf_files = cpf_download('ajisai','2007-06-01 11:30:00')
    dir_cpf_files = cpf_download(['ajisai','lageos1','hy2a'],'2007-06-01 11:30:00','EDC')

    Parameters:
    satnames -> [str, str list, or None, default = None] target name or list of target names. If None, then all feasible targets at the current moment will be downloaded. In this case, 'date' must also be None. 
    date -> [str or None, default = None] 'iso-formatted' time, such as '2017-12-20 05:30:00'. It specifies a moment before which the latest CPF ephemeris files are downloaded. If None, then all feasible targets or targets in list at the current moment will be downloaded.
    source -> [str, default = 'CDDIS'] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    append ->[Bool, default = False] If False, clear the data storage directory ahead of requesting CPF files. If True, then keep the data storage directory.
    
    Outputs:
    dir_cpf_files -> [str list] list of paths for CPF ephemeris files in user's local directory

    Note: if 'date' is provided, namely not None, then 'satnames' must also be provided.
    '''   
    cpf_files_downloaded, cpf_files_missed = cpf_download_prior(satnames,date,source,append)
    
    if cpf_files_missed:
        cpf_files_downloaded2, cpf_files_missed2 = cpf_download_prior(cpf_files_missed,append=True)
        cpf_files_downloaded += cpf_files_downloaded2
    return cpf_files_downloaded    

def get_cpf_filelist(server,dir_cpf_from,mode):    
    '''
    Generate CDDIS CPF files list sorted by date from the latest to the oldest
    '''
    res = requests.get(server + dir_cpf_from)
    soup = BeautifulSoup(res.text, 'html.parser')

    # extract time infomation
    time_info = soup.find_all('span')
    if mode == 'bycurrent':
        time_list = [ele.get_text().split('  ')[0] for ele in time_info][2:] # Remove two extra items
    elif mode == 'bydate':
        time_list = [ele.get_text().split('  ')[0] for ele in time_info]    
    n_time_list = len(time_list)

    # extract filename infomation
    filename_info = soup.find_all('a')
    cpf_files_list_unsort = [ele.get_text() for ele in filename_info if '_cpf_' in ele.get_text()]
    n_cpf_files_list_unsort = len(cpf_files_list_unsort)

    if n_time_list != n_cpf_files_list_unsort:
        raise Exception('Timestamp and CPF files are not matched!')

    cpf_files_dict = dict(zip(cpf_files_list_unsort,time_list))    
    cpf_files_turple = sorted(cpf_files_dict.items(), key=lambda x: x[1],reverse=True) # Sort by release time
    cpf_files_list = [ele[0] for ele in cpf_files_turple]

    res.close()
    return cpf_files_dict, cpf_files_list   
