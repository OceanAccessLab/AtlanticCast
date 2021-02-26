from netCDF4 import Dataset
import os, sys, re, pandas
import numpy as np

import time
# for timing purposes, define start = time.time() and end = time.time(), and print(end-start)
# to see time spent doing something 

# figure out what file format exists in this folder
# defualt: no binning, but passing a parameter will change the binning value
def cnv2netCDF(root_directory, regex_dict = None, binning = 0):
    # .cnv files are processed at varying levels, we will focus on the least processed ones but we keep the following for potential future uses
    # create array for each level of processing currently known, and add to array each corresponding file
    CNV_data_converted = []
    CNV_data_converted_filtered = []
    CNV_data_converted_filtered_loop_edited = []
    CNV_data_converted_filtered_loop_edited_derived = []
    CNV_data_converted_filtered_loop_edited_derived_averaged = []

    for file in os.listdir(root_directory):
        if file.endswith("converted.cnv"):
            CNV_data_converted.append(file)
        elif file.endswith("convertedfiltered.cnv"):
            CNV_data_converted_filtered.append(file)
        elif file.endswith("convertedfilteredloop_edited.cnv"):
            CNV_data_converted_filtered_loop_edited.append(file)
        elif file.endswith("convertedfilteredloop_editedderived.cnv"):
            CNV_data_converted_filtered_loop_edited_derived.append(file)
        elif file.endswith("convertedfilteredloop_editedderivedbinned.cnv"):
            CNV_data_converted_filtered_loop_edited_derived_averaged.append(file)
        # add any other file format we want to process

    # we want to have all the data from a unique trip together in the new netCDF4 file
    # we do this by assuming that metadata from different files is the same, ie no new variable is added/modified
    # we can also now ignore span since this data is not accurate anymore
    # alternatively, we can create individual .nc files for each .cnv file, and turn it into a multi-file netCDF dataset   
    # for each file that we found that is in CNV_data_converted, start processing
    metadata = {}
    sensors = {}
    this_is_a_memory_hog = []
    this_is_a_memory_hog = np.array(this_is_a_memory_hog)
    for file in CNV_data_converted:
        with open(str(root_directory) +'\\' +str(file),"r") as fi:
            for ln in fi:
                # metadata
                if ln.startswith('*') or ln.startswith('# nvalues') or ln.startswith('# nquan'):
                # regex and parse values in regex_dict 
                    key, match = _parse_line(ln, regex_dict)
                    for entry in regex_dict.keys():
                        if entry == key:
                            metadata.update({str(key): match.group(str(key))})
                            
                # select lines with info about the sensors
                # sensor and variable data
                elif ln.startswith('#'):
                    if ln.startswith("# name"):
                        ctd_var = None
                        units = None
                        try :
                            ctd_var = ln.split('=')[1].strip().split(':')[1].split('[')[0].strip()
                            units = ln.split('=')[1].strip().split(':')[1].split('[')[1][:-1]
                            sensors.update( {
                                ln.split('name ')[1].split('=')[0].strip() : {
                                    'CTD_VAR': ctd_var,
                                    'CTD_VAR_CODE': ln.split('name ')[1].split('=')[1].split(':')[0].strip(), 
                                    'UNITS': units    }})
                        except: continue

                    # elif ln.startswith("# span"):
                    #     minimum = None
                    #     maximum = None
                    #     try :
                    #         minimum = ln.split('=')[1].split(',')[0].strip()
                    #         maximum = ln.split('=')[1].split(',')[1].strip()
                    #         sensors[ln.split('span ')[1].split('=')[0].strip()].update( {
                    #             'min': minimum,
                    #             'max': maximum  })
                    #     except: continue
                else: 
                    # read the data
                    # print(ln.split())
                    np.append(this_is_a_memory_hog, list(ln.split()), axis=0)
                    # print(this_is_a_memory_hog)
                    # for i in range(0, len(ln.split())):
                        # print(ln.split())
                        # this_is_a_memory_hog[i].append(ln.split)
                    # print(ln.split())
                    # continue

    print(this_is_a_memory_hog)
    # now, we should have a giant pandas dataframe with all the data, and the corresponding metadata
    # here, create a new NetCDF4 file
    netCDF = Dataset(str(root_directory) + '.nc', 'w', format='NETCDF4')
    # sample file only contains 2 dimensions, this is what we're going to start with, and with unlimited size
    time = netCDF.createDimension('time', None)
    level = netCDF.createDimension('level', None)

    # create coordinate variables
    times = netCDF.createVariable("time","f8",("time",))
    levels = netCDF.createVariable("level","i4",("level",))

    latitudes = netCDF.createVariable('latitude', np.float32, ('time'), zlib=True)
    longitudes = netCDF.createVariable('longitude', np.float32, ('time'), zlib=True)
    # sounder_depths = netCDF.createVariable('sounder_depth', np.float32, ('time'), zlib=True)

    # for each data column, create a corresponding variable
    for value in sensors:
        # print(sensors[value])
        var_name = None
        var_name = sensors[value]['CTD_VAR'].replace(' ', '_').split(',')[0].lower()
        try:
            globals()[value] = netCDF.createVariable( var_name, np.float32, ('level'), zlib=True, fill_value=-9999)
        except:
            print('ISSUE: name in use, will be fixed with multithreading as it will use different memory spaces')
            return None
    # print(netCDF)
        # print(var_name)
        # sensors[value]
        # print(sensors[value])

        #     try:
        #         variables[var_name] = [
        #             netCDF.createVariable(var_name, np.float32, ('level'), zlib=True, fill_value=-9999), name]
        #     except:
        #         continue
            # globals()[]
            # dimensions[]
            # print(key)
        # print(netCDF)

        # print(sensors['5'])
            # print(sensors)
            # end = time.time()
            # print(end-start)
            # print(metadata)
        
            # continue here



        # netCDF.close()
    # print('==========================================')
    # print('new file')
    return None


# def pfile2netCDF():
#     return None


# NEEDED
def _parse_line(line, rx_dict):
    for key, rx in rx_dict.items():
        match = rx.search(line)
        # print(match)
        if match:
            # print(key, match)
            return key, match
    # if there are no matches
    return None, None