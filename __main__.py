# Notes
# .cnv are pretty much just json/xml file format, easily parsed and compiled
# .bl seems like system logs
# .hdr seems like sensor info
# .hex raw sensor input
# .xmlcon is description of data types
# .wkz/.wr1/.sav unreadable 
# .d99 is pretty much just pfile format
# .h99 hex i think? 
# .vld unreadable
# Questions
# demander a Max/Fred quelle est la différence dans le format de fichier (si il y en a) entre les pfiles et 
# et les données sources CTD (.d99, .d09)
# A tester
#  performance improvements between arrays/dicts
#  performance improvements compiling using Cython/other Python compiler
# bin by pressure average 1 meter
# rajouter le nom du fichier en tant que variable dans le netCDF
# var météo

from netCDF_generator import cnv2netCDF

import os, re
import pandas as pd
dir = os.path.abspath('.')

# add to this array any file extension we want to analyze
ext = ['.cnv', '.pfile']

folders_to_explore = {}
for entry in ext:
    folders_to_explore.update({entry[1:]: {}})

## Will implement later
# implement the pandas for parsing header files in data files
# global regex_dict
regex_dict = {
    # 'school': re.compile(r'School = (?P<school>.*)'),
    'software_version': re.compile(r'Software Version (?P<software_version>.*)'),
    'temperature_sn': re.compile(r'Temperate SN = (?P<temperature_sn>.*)'), 
    'conductivity_sn': re.compile(r'Conductivity SN = (?P<conductivity_sn>.*)'), 
    'bytes_per_scan': re.compile(r'Number of Bytes Per Scan = (?P<bytes_per_scan>.*)'), 
    'voltage_words': re.compile(r'Number of Voltage Words = (?P<voltage_words>.*)'), 
    'averaged_scans': re.compile(r'Number of Scans Averaged by the Deck Unit = (?P<averaged_scans>.*)'), 
    'sys_upload_time': re.compile(r'System UpLoad Time = (?P<sys_upload_time>.*)'), 
    'nmea_lat': re.compile(r'NMEA Latitude = (?P<nmea_lat>.*)'), 
    'nmea_long': re.compile(r'NMEA Longitude = (?P<nmea_long>.*)'), 
    'nmea_time': re.compile(r'NMEA UTC (Time) = (?P<nmea_time>.*)'), 
    'ship': re.compile(r'Ship: (?P<ship>.*)'), 
    'station': re.compile(r'Station: (?P<station>.*)'), 
    'operator': re.compile(r'Operator: (?P<operator>.*)'),
    'nquan': re.compile(r'nquan = (?P<nquan>.*)'),
    'nvalues': re.compile(r'nvalues = (?P<nvalues>.*)'),
    'interval': re.compile(r'interval = (?P<interval>.*)'),
    'start_time': re.compile(r'start_time = (?P<nvalues>.*)')    }


## This whole part may not be necessary, but could be useful in the future, so it is kept for modularity purposes
# navigate the current file directory, and for each file type specified in
for root, dirs, files in os.walk(dir): 
    for entry in ext:
        # for each folder, create a dict entry with key: folder address, and value an empty array
        folders_to_explore[entry[1:]].update({str(root):[]})
        for file in files: 
            # if a file is found with an extension specified in the ext array, then add to the corresponding dict entry 
            # along with the full folder address  and file name
            if file.endswith(entry):
                # if the file inside the folder has extension .cnv, add it to the corresponding dict entry 
                folders_to_explore[entry[1:]][str(root)].append(file)
        

# create a NetCDF file for each folder: uses all the data file within a folder (for a trip) 
# for now, we will focus on the .cnv files
# if a folder entry in the dict exists and is non-empty, call the next function (to initiate the netCDF4 file creation process) in a new thread
for key in folders_to_explore['cnv'].keys():
    if folders_to_explore['cnv'][key]:
        cnv2netCDF(key, regex_dict)
