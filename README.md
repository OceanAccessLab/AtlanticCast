# atlanticcast
A CFER-DFO project to convert historical Atlantic Coast CTD casts into a NetCDF data product.


# Default behavior
## By default, the program will create a NetCDF file with name the folder it is located in, containing compatible data found in subfolders.
- Explore root folder (folder from where the program was called)
- Recursively explore sufolders, and resolve only for compatible file extensions
- Generate unique NetCDF file at root folder lever.
	- For each compatible file formats
		- for each expedition folder
			- for each expedition ID
				- create a subgroup 
- complete binning over 1m
- convert DMS lag/lon to DD lat/lon
- convert date time to float date from 1900-01-01 00:00:00


# Install executions
- Preferably, createa a new virtualenv 
- Ensure the following dependencies are installed
	- netCDF4
	- numpy
	- pandas 
- Move `__main__.py` to the appropriate destination (ie, `2001`)
	- Preferably, make sure the folder containing data samples is named correctly (the name of the mission) as that is what they program wil use to create the subgroups
- Execute the program
- You should find a new file, named according to the folder that contains the program, with extension `.nc`


## Subgroup attributes
- mission_id
- lat/lon data
- timestamp


## How to read
- use the following snippet to create a generator, and then iterate over items to get data
```
ROOT_NCFILE = Dataset('filename.nc', 'r', format='NETCDF4')

def walktree(ncfile):
    values = ncfile.groups.values()
    yield values
    for value in ncfile.groups.values():
        for children in walktree(value):
            yield children

for item in walktree(ROOT_NCFILE):
    print(item)	
```
- alternatively, use `ncdump`


# To-Do
- try to integrate (cioos-data-transform)[https://github.com/cioos-siooc/cioos-siooc_data_transform] for .cnv file conversion
	- files are already tagged, 
- fix sensor metadata to comply with CF 1.8 (lack of source data makes it hard to evaluate the proper type 
- add proper attributes to NetCDF file (under `if __name__ == '__main__':` )
