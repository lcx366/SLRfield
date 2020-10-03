from os import remove
import requests
from tqdm import tqdm
from colorama import Fore
from time import sleep

def tqdm_ftp(ftp,dir_cpf_to,cpf_file):
    '''
    Try to download files from remote server by ftp.
    '''
    total_size = int(ftp.size(cpf_file))
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)
    desc = 'Downloading {:s}'.format(cpf_file)
    missing_flag = False
    for idownload in range(5):
        try:
            local_file =  open(dir_cpf_to + cpf_file, 'ab')
            pos = local_file.tell()
            pbar = tqdm(desc = desc,total=total_size,unit='B',unit_scale=True,position=0,initial=pos,bar_format=bar_format)
            def progressbar(chunk):
                local_file.write(chunk)
                pbar.update(len(chunk))
            res = ftp.retrbinary('RETR ' + cpf_file, progressbar, rest=pos) # RETR is an FTP command
            break       
        except:
            sleep(3)
            if idownload == 4:
                remove(dir_cpf_to + cpf_file)
                print('No response, skip {:s}'.format(cpf_file))
                missing_flag = True
        finally:
            pbar.close()
            local_file.close()  
            if missing_flag: 
                return cpf_file  
            else:
                return None     


def tqdm_request(url,dir_cpf_to,cpf_file):
    '''
    Try to download files from remote server by request.
    '''
    block_size = 1024*10
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)
    desc = 'Downloading {:s}'.format(cpf_file)
    missing_flag = False
    for idownload in range(5):
        try:
            local_file = open(dir_cpf_to + cpf_file, 'wb')
            pos = local_file.tell()
            res = requests.get(url,stream=True,timeout=200)
            total_size = int(res.headers.get('Content-Length'))
            pbar = tqdm(desc = desc,total=total_size,unit='B',unit_scale=True,bar_format = bar_format,position=0,initial=pos)
            for chunk in res.iter_content(block_size):
                local_file.write(chunk)  
                pbar.update(len(chunk))   
            pbar.close()   
            res.close()  
            break
        except: 
            sleep(3)
            if idownload == 4:
                remove(dir_cpf_to + cpf_file)
                print('No response, skip {:s}'.format(cpf_file)) 
                missing_flag = True
        finally:    
            local_file.close() 
            if missing_flag: 
                return cpf_file  
            else:
                return None      
                      
