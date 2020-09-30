# atlanticcast
A CFER-DFO project to convert historical Atlantic Coast CTD casts into a NetCDF data product.


# Requirements
I recommend using the `python-pipenv` to create a new virtual environment, and use `pipenv sync` to make sure all members are using the same version plugin and interpreter.

# Description
I think it would be a good idea to implement multi-threading here since it will be a minimal amount of work for a significant performance improvement, and the amount of work required to do it is not monstruous. 


## `pfiles.py`
This file declares the new object class `pfiles`, contains a parser function and a reader function.

## `netcdfWriter.py`
Takes a `pfiles` Object as input and inserts into a specified NetCDF file.

## `__main__.py`
Initializes all the dependencies and imports needed libraries,  opens 2 new processes: 
- one will iterate over the list of files in the `*.list` file, and for every file create a new `pfiles` object and push it in a FIFO stack
- one will grab every item in the FIFO stack and append to a NetCDF file generated using the `netCDF4` library.