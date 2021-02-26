import os

class pfiles():
    def __init__(self, inputFile):
        self.id = ''            # header[0]
        self.latitude = ''      # header[1] is degrees, whole number of header[2] is minutes, decimal number of header[2] is seconds
        self.longitude = ''     # header[3] is degrees, whole number of header[4] is minutes, decimal number of header[4] is seconds
        self.date = ''          # header[5], in YYYY-MM-DD format
        self.time = ''          # header[6], in HH:SS military time
        self.sounder = ''       # header[7]
        self.instid = ''        # header[8]
        self.set = ''           # header[9]
        self.insttype = ''      # header[10], if 'S' then "V", elif 'XBT' then "F", elif 'CTD' then "V"
        self.comment = ''       # header[11], if empty then just spaces, so check if maybe issue?
        self.data = ''          # will be fancy pandas.dataframe, multi-dimension
        self.columns = ''        # array of column names
        self.parseData(inputFile)


    def parseData(self, inputFile):
        # iterates over inputFile and adds to corresponding field in object self
        file = open(inputFile, 'r', encoding="utf8", errors='ignore') 
        if 'NAFC_Y2K_HEADER' not in file.readline():
            error_msg = 'Problem with file: header [skip]'
            print(error_msg)
            expr = 'echo ' + inputFile + ' : ' + error_msg +' >> .netcdfgen_log.txt'
            os.system(expr)
            return None

        cast_info = file.readline().split()
        self.id = cast_info[0]
        self.latitude = cast_info[1] + cast_info[2].split('.')[0]/60 + cast_info[2].split('.')[1]/3600
        self.longitude = cast_info[3] + cast_info[4].split('.')[0]/60 + cast_info[4].split('.')[1]/3600
        self.date = '' ## convert using date2num from the netCDF4 package
        self.time = '' ## convert using date2num from the netCDF4 package
        self.sounder = cast_info[7]
        self.instid = cast_info[8]
        self.set = cast_info[9]
        self.insttype = 'V' if cast_info[10] == 'S' elif 'F' if cast_info[10] == 'XBT' elif 'V' if cast_info[10] == 'CTD'
        self.comment = ''
        self.columns = inputFile.readline.split()

        # restructure using recursive maybe? have to check best performance
        if np.size(data) == 0: # empty files
            error_msg = 'Empty file [continue]'
            print(error_msg)
            expr = 'echo ' + filename + ' : ' + error_msg +' >> emptyfile_problems.txt'
            os.system(expr)
            df = pd.DataFrame([])
        elif np.ndim(data) < 2: # In some files, there is no line skip (all data in one line)
            error_msg = 'Wrong datafile dimension [continue]'
            print(error_msg)
            expr = 'echo ' + filename + ' : ' + error_msg +' >> emptyfile_problems.txt'
            os.system(expr)
            df = pd.DataFrame([])
        elif np.shape(data)[1] == np.size(columns): # same shape
            df = pd.DataFrame(data, columns=columns, dtype=float)
        elif (np.shape(data)[1]==9) & (np.size(columns)==10): # very likely ph problem
            columns = columns[0:-1]
            df = pd.DataFrame(data, columns=columns, dtype=float)
            error_msg = 'Missing pH columns [continue]'
            print(error_msg)
            expr = 'echo ' + filename + ' : ' + error_msg +' >> ph_problems.txt'
            os.system(expr)

    
    
        