# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 11:12:47 2015

@author: Julia
"""
from dropbox.client import DropboxClient
import xray

DROPBOX_APP_KEY = 'w60h88jagrapjkw'
DROPBOX_APP_SECRET = 'sxmj60mm1opfdcd'
access_token = 'JGWZ6z0FSMkAAAAAAAAAkNukhKdp7pgVvrAxvs5ZoKt7QDoSpsjXTAKpyLuEjDyU'
dropbox_dir = '/Kenyalab/Data/Tower/TowerData/raw_netCDF_output/'



def find_files(year=None, doy=None):
    import os
    from posixpath import join
    #dropbox_dir = os.environ.get('DROPBOX_DIR')
    files = []  # Initialize an empty array
    f = 'raw_MpalaTower_%i_%03d.nc' % (year, doy)
    for this_file in File.DATA_FILES:
        try:
            temp_location = write_temp(dropbox_dir)
        except:
            continue
        this_file = File(
            filename=f,
            datafile=this_file,
            file_location=temp_location,
        )
        files.append(this_file)
    return files



def write_temp(dropbox_dir):
    from dropbox.client import DropboxClient
    
    client = DropboxClient(access_token)
    file_location = join(dropbox_dir, datafile, filename)
    temp_location = join('/temp', datafile, filename)
    out = open(temp_location, 'wb')
    with client.get_file(file_location) as f:
        out.write(f.read())
    out.close()
    return temp_location


def get_netcdf():
    for File in this_metadata.files:
        client.share(File.file_location)
