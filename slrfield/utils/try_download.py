import wget

def wget_download(url,dir_file,desc=None):
    """
    download files by wget command

    Inputs:
        url -> [str] URL of the file to be downloaded
        dir_file -> [str] path of the file to be downloaded
        desc -> [str,optional] description of the downloading   
    Outpits:
        wget_out -> [str] path of the file downloaded

    """
    if desc: print(desc)
    wget_out = wget.download(url,dir_file)
    print()

    return wget_out