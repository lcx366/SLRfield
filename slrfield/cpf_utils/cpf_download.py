from os import system,path,remove,makedirs
from ftplib import FTP
from astropy.time import Time
import time as pytime

def download_bycurrent(source,satnames):
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

    Outputs:
    server -> [str] server for downloading CPF ephemeris files. Currently, only 'cddis.nasa.gov' and 'edc.dgfi.tum.de' are available.
    dir_cpf_from -> [str] directory for storing CPF ephemeris files in remote server.
    dir_cpf_to -> [str] user's local directory for storing CPF ephemeris files
    cpf_files -> [str list] list of CPF ephemeris files
    '''   
    cpf_files = []
    date = Time.now().iso
    dir_cpf_from = '~/slr/cpf_predicts//current/'
    dir_cpf_to = 'CPF/'+source+'/'+date[:10] + '/'
    if not path.exists(dir_cpf_to): 
        makedirs(dir_cpf_to)   
    else:
        system('rm -rf %s/*' % dir_cpf_to)
        
    if source == 'CDDIS':
        server = 'cddis.nasa.gov' 
    elif source == 'EDC':
        server = 'edc.dgfi.tum.de'
    else:    
        raise Exception("Currently, for CPF prediction centers, only 'CDDIS' and 'EDC' are available.")    
    
    ftp = FTP(server)
    ftp.login()
    ftp.cwd(dir_cpf_from)
    cpf_files_list = ftp.nlst('-t','*cpf*') # list files containing 'cpf' from newest to oldest   
        
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
    ftp.quit()  
    ftp.close()  
    return server,dir_cpf_from, dir_cpf_to,cpf_files                   

def download_bydate(source,date,satnames): 
    '''
    Download the latest CPF ephemeris files before a specific time.

    Usage: 
    server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bydate('CDDIS','2007-06-01 11:30:00',['ajisai','lageos1','hy2a'])
    server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bycurrent('EDC','2017-12-20 05:30:00','hy2a'])

    Inputs:
    source -> [str] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    date -> [str] 'iso-formatted' time, such as '2017-12-20 05:30:00'. It specifies a moment before which the latest CPF ephemeris files are downloaded.
    satnames -> [str, str list] target name or list of target names. 

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
    if not path.exists(dir_cpf_to): makedirs(dir_cpf_to) 
        
    if source == 'CDDIS':
        server = 'cddis.nasa.gov'                
    elif source == 'EDC':
        server = 'edc.dgfi.tum.de'                         
    else:    
        raise Exception("Currently, CPF predictions only from 'CDDIS' and 'EDC' are available.")     
        
    ftp = FTP(server)    
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
    return server,dirs_cpf_from, dir_cpf_to,cpf_files

def cpf_download(satnames = None,date = None,source = 'CDDIS'):
    '''
    Download the latest CPF ephemeris files.

    Usage: 
    dir_cpf_files = cpf_download()
    dir_cpf_files = cpf_download(source = 'EDC')
    dir_cpf_files = cpf_download('lageos1')
    dir_cpf_files = cpf_download('ajisai','2007-06-01 11:30:00')
    dir_cpf_files = cpf_download(['ajisai','lageos1','hy2a'],'2007-06-01 11:30:00','EDC')

    Parameters:
    satnames -> [str, str list, or None, default = None] target name or list of target names. If None, then all feasible targets at the current moment will be downloaded. 
    In this case, 'date' must also be None. 
    date -> [str or None, default = None] 'iso-formatted' time, such as '2017-12-20 05:30:00'. It specifies a moment before which the latest CPF ephemeris files are downloaded.
    If None, then all feasible targets or targets in list at the current moment will be downloaded.
    source -> [str, default = 'CDDIS'] source for CPF ephemeris files. Currently, only 'CDDIS' and 'EDC' are available.
    
    Outputs:
    dir_cpf_files -> [str list] list of paths for CPF ephemeris files in user's local directory

    Note: if 'date' is provided, namely not None, then 'satnames' must also be provided.
    '''

    dir_cpf_files = []
    
    if date is None:
        server,dir_cpf_from, dir_cpf_to,cpf_files = download_bycurrent(source,satnames)  
        ftp = FTP(server)    
        ftp.login()  
        ftp.cwd(dir_cpf_from) 
        for cpf_file in cpf_files:
            try_download(ftp,dir_cpf_from,dir_cpf_to,cpf_file)
            dir_cpf_files.append(dir_cpf_to+cpf_file)
                
    else:    
        server,dirs_cpf_from, dir_cpf_to,cpf_files = download_bydate(source,date,satnames)    
        ftp = FTP(server)    
        ftp.login()  
    
        for dir_cpf_from,cpf_file in zip(dirs_cpf_from,cpf_files):
            ftp.cwd(dir_cpf_from) 
            try_download(ftp,dir_cpf_from,dir_cpf_to,cpf_file)
            dir_cpf_files.append(dir_cpf_to+cpf_file)
                           
    ftp.quit()  
    ftp.close()

    return dir_cpf_files

def try_download(ftp,dir_cpf_from,dir_cpf_to,cpf_file):
    '''
    Download the CPF ephemeris files into the user's local directory from remote server.
    '''
    print('Downloading ... ',cpf_file,end=' ... ')
    # If the download fails, try to download 3 times
    for idownload in range(3):
        try:
            with open(dir_cpf_to + cpf_file, 'wb') as local_file:
                res = ftp.retrbinary('RETR ' + dir_cpf_from + cpf_file, local_file.write) # RETR is an FTP command
                print(res)
                local_file.close()   
                break
                   
        except:
            local_file.close()
            remove(dir_cpf_to + cpf_file)
            if idownload == 2: raise Exception('Server did not respond, file download failed') 
            pytime.sleep(20)    
                            