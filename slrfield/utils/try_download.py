from os import remove
from tqdm import tqdm
from colorama import Fore
from time import sleep
import requests
from ftplib import all_errors


def tqdm_ftp(ftp, dir_to, file, desc):
    """
    Try to download files from remote server by ftp with a colored progress bar
    """
    dir_file = dir_to + file
    total_size = int(ftp.size(file))
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)

    for idownload in range(5):
        try:
            local_file = open(dir_file, 'wb')
            pos = local_file.tell()
            pbar = tqdm(desc=desc, total=total_size, unit='B', unit_scale=True,
                        position=0, initial=pos, bar_format=bar_format)

            def progressbar(chunk):
                local_file.write(chunk)
                pbar.update(len(chunk))
            # RETR is an FTP command
            ftp.retrbinary('RETR ' + file, progressbar)
            break
        except all_errors:
            sleep(2)
            if idownload == 4:
                remove(dir_file)
                print('No response, skip {:s}'.format(file))
        finally:
            pbar.close()
            local_file.close()


def tqdm_request_http(url, dir_cpf_to, cpf_file, desc):
    """
    Try to download CPF or OEP files from url with a colored progress bar.
    """
    block_size = 1024*10
    missing_flag = False
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)
    for idownload in range(5):
        try:
            local_file = open(dir_cpf_to + cpf_file, 'wb')
            pos = local_file.tell()
            res = requests.get(url, stream=True, timeout=200, headers={
                               'Accept-Encoding': None,
                               'Range': f'bytes={pos}-'})
            res.raise_for_status()
            total_size = int(res.headers.get('Content-Length'))
            pbar = tqdm(desc=desc, total=total_size, unit='B', unit_scale=True,
                        bar_format=bar_format, position=0, initial=pos)
            for chunk in res.iter_content(block_size):
                local_file.write(chunk)
                pbar.update(len(chunk))
            pbar.close()
            res.close()
            break
        except (requests.HTTPError,
                requests.ConnectionError,
                requests.Timeout) as e:
            sleep(3)
            if idownload == 4:
                remove(dir_cpf_to + cpf_file)
                print(f'No response {str(e)}, skip {cpf_file}')
                missing_flag = True
        finally:
            local_file.close()

    if missing_flag:
        return cpf_file
    else:
        return None
