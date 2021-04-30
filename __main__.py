from netCDF4 import Dataset
from cftime import date2num
from datetime import datetime
# import ios_data_transform as iod
import numpy as np
import os, re, sys, json, requests, pandas
from xml.dom import minidom

def process_dataset(dataset):
    ## Converts timestamp to float time
    try:
        dataset['time'] = dataset['time'].apply(lambda x: date2num(datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'), 'days since 1900-01-01'))
    except:
        print('No "Time" column, no need to convert datetime format.')

    ## remove scan column
    if 'scan' in dataset.columns:
        del dataset['scan']

    ## converts every line of the dataset to numeric type
    ## if error ocurs, replace value with NaN
    for columns in dataset.columns:
        if columns == 'time':
            continue
        dataset[columns] = pandas.to_numeric(dataset[columns], errors='coerce')
    ## bin by 1m depth
    step = 1  ## change here for different bin
    dz = np.arange(dataset['depth'].min(), dataset['depth'].max(), step)
    binned_dataset = dataset.groupby(pandas.cut(dataset['depth'], dz, labels=False), as_index=False).mean()
    binned_dataset['depth'] = dz[:-1]
    
    return binned_dataset

def convert_lats_lon(DMS_lats_lon):
    ## Converts lat-lon data from DMS to decimal, based on the sign of the degree value
    if int(DMS_lats_lon[0]) > 0: 
        lat = int(DMS_lats_lon[0]) + int(DMS_lats_lon[1].split('.')[0])/60 + int(DMS_lats_lon[1].split('.')[1])/3600*0.6
    else:
        lat = - int(DMS_lats_lon[1].split('.')[1])/3600*0.6 - int(DMS_lats_lon[1].split('.')[0])/60 + int(DMS_lats_lon[0])
    if int(DMS_lats_lon[2]) > 0: 
        lon = int(DMS_lats_lon[2]) + int(DMS_lats_lon[3].split('.')[0])/60 + int(DMS_lats_lon[3].split('.')[1])/3600*0.6
    else:
        lon = - int(DMS_lats_lon[3].split('.')[1])/3600*0.6 - int(DMS_lats_lon[3].split('.')[0])/60 + int(DMS_lats_lon[2])
    return lat, lon 

def folder_explorer(root_path = None ):
    ## Recursively explores folders and subfolders to find compatible files
    ## Add compatible files found to MASTER_TABLE
    files = []
    ## analyze files contained inside `folder_name`    
    for name in os.listdir(root_path):
        # print(name)
        if os.path.isdir(os.path.join(root_path, name)):
            folder_explorer(os.path.join(root_path, name))
        else:
            trip_details = {}
            if re.search('_data.txt', name):
                trip_details.update({
                    'root_folder': root_path, 
                    'data': name, 
                    'metadata': name.replace('_data.txt', '_metadata.txt')})
                MASTER_TABLE['concerto'].append(trip_details)
            elif re.search(r"(\.D)[0-9]+", name):
                trip_details.update({
                    'root_folder': root_path, 
                    'data': name })
                MASTER_TABLE['y2k'].append(trip_details)
            elif re.search('.cnv', name):
                trip_details.update({
                    'root_folder': root_path, 
                    'data': name })
                MASTER_TABLE['cnv'].append(trip_details)

def concerto2ncfile(parameterFile):
    if not parameterFile:
        return
    ROOT_NCFILE = Dataset(CURR_PATH.split('\\')[-1]+'.nc', 'a', format='NETCDF4')
    uniqueTrip = ROOT_NCFILE.createGroup("concerto/" + parameterFile['root_folder'].split('\\')[-1])
    uniqueTrip.createDimension("time", None)
    uniqueTrip.createDimension("level", None)

    json_metadata = open(os.path.join(parameterFile['root_folder'], parameterFile['metadata']) )
    unpacked_metadata = json.load(json_metadata)

    for vars in unpacked_metadata['dataheader']:
        if vars['name'] == 'Time':
            uniqueTrip.createVariable("time", "f8", ('time',))
            continue
        if vars['name'] == 'Depth':
            depth = uniqueTrip.createVariable('depth', 'i4', ('level',))
            depth.units = vars['units']
            continue
        ## here, we're giving all the variables the default dimension of 'depth'
        var = uniqueTrip.createVariable(vars['name'].lower(), 'f4', ('level',))
        var.units = vars['units']

    dataset = pandas.read_csv(os.path.join(parameterFile['root_folder'], parameterFile['data']))    
    dataset.columns = dataset.columns.str.lower()    
    binned_dataset = process_dataset(dataset)
    for vars in uniqueTrip.variables:
        uniqueTrip[vars.lower()][:] = binned_dataset[vars.lower()]
    ROOT_NCFILE.close()

def y2k2ncfile(parameterFile):
    ## if file does not have NAFC_Y2K header, drop the file
    datafile = open(os.path.join(parameterFile['root_folder'], parameterFile['data']))
    line = datafile.readline().strip() 
    if line != 'NAFC_Y2K_HEADER':
        return
    header = []
    columns = []
    data = []
    ## append line to either header or data
    _header = True
    while line :
        line = datafile.readline()
        if line.strip() == '-- DATA --':
            _header = False
            # continue allows us to skip the '--DATA--' line
            continue
        if _header:
            header.append(line.strip().split())
        else:
            # skip empty line, usually last line
            if len(line.strip().split()) == 0:
                continue
            data.append(line.strip().split())

    # last line before data is the name of columns, so by .pop() we assign it and remove it from header[]
    columns = header.pop()
    mission_details = header[0]

    ## instantiate the dataframe, complete preprocessing
    dataset = pandas.DataFrame(data, columns=columns)
    binned_dataset = process_dataset(dataset)

    ## add subgroup corresponding to `mission name/mission_id` 
    ## mission_name is found from folder containing file
    ## mission_id is found in header file
    ROOT_NCFILE = Dataset(CURR_PATH.split('\\')[-1]+'.nc', 'a', format='NETCDF4')
    uniqueTrip = ROOT_NCFILE.createGroup("y2k/" + parameterFile['root_folder'].split('\\')[-1] + '/'+ mission_details[0])
    # add attributes to group, also adding mission_id as an attribute
    uniqueTrip.latitude, uniqueTrip.longitude = convert_lats_lon(mission_details[1:5]) 
    uniqueTrip.timestamp = date2num(datetime.strptime(mission_details[5] + ' ' + mission_details[6], '%Y-%m-%d %H:%M'), 'days since 1900-01-01')
    uniqueTrip.mission_id = mission_details[0]

    # if dimensions dont exist already, create them
    try:
        uniqueTrip.createDimension("levels", None)
        uniqueTrip.createDimension("latitudes", None)
        uniqueTrip.createDimension("longitudes", None)
    except:
        print('Dimension already exists for this subgroup / expedition')    
    
    ## Try creating the corresponding variables 
    for vars in binned_dataset.columns:
        var = None
        try:
            if vars == 'lat':
                var = uniqueTrip.createVariable(vars, 'f4', ('latitudes'))
                var.units = "degree_north"
                var.long_name = 'latitude'                
            elif vars == 'lon':
                var = uniqueTrip.createVariable(vars, 'f4', ('longitudes'))
                var.units = "degree_east"
                var.long_name = 'longitude'
            elif vars == 'depth':
                var = uniqueTrip.createVariable(vars, 'f4', ('levels'))
                var.units = "m"
                var.long_name = 'depth'
            else:
                var = uniqueTrip.createVariable(vars, 'f4', ('levels',))
                ## add attributes from http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml
        except:
            print('Variable '+vars+' already exists.')

    ## assign values to variables
    for vars in uniqueTrip.variables:
        uniqueTrip[vars][:] = binned_dataset[vars]
    ROOT_NCFILE.close()

def main(parameters):
    # explore root folder, ie folder from where the file was executed
    folder_explorer(root_path= CURR_PATH)

    ## For all files files with compatible data format found, create a corresponding subgroup in the NetCDF file, and add data

    if len(MASTER_TABLE['concerto']) != 0:
        for params in MASTER_TABLE['concerto']:
            concerto2ncfile(params)
    
    if len(MASTER_TABLE['y2k']) != 0:
        for params in MASTER_TABLE['y2k']:
            y2k2ncfile(params)


if __name__ == '__main__':
    global CURR_PATH
    CURR_PATH = os.getcwd()

    global MASTER_TABLE
    MASTER_TABLE = {
        'concerto' : [], 
        'y2k': [], ## Y2K header, so .Dxx files
        'cnv': []
        }

    ## started work on parsing data from CF Convention for sensor attributes
    ## halted due to lack of information from source data
    # try:
    #     xml = open('cf-standard-name-table.xml', 'r')
    # except:
    #     URL = "http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml"
    #     xml = requests.get(URL)
    #     print(xml)
    #     with open('cf-standard-name-table.xml', 'wb') as file:
    #         file.write(response.content)
    # global CF_CONVENTION_STANDARD_NAME
    # CF_CONVENTION_STANDARD_NAME = minidom.parse(xml)
    # print(CF_CONVENTION_STANDARD_NAME)


    ROOT_NCFILE = Dataset(CURR_PATH.split('\\')[-1]+'.nc', 'w', format='NETCDF4')
    ROOT_NCFILE.description = 'Merger of all files contained in folder ' + str(CURR_PATH.split('\\')[-1])
    ROOT_NCFILE.institution = ''  ## Set these accordingly
    ROOT_NCFILE.summary = ''
    ROOT_NCFILE.title = ''

    ROOT_NCFILE.close()
    main(sys.argv[1:])