class pfiles():
    def __init__(self):
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
        self.data = ''          ## will be fancy pandas.dataframe, multi-dimension

                
    def parseData(self, inputFile):
        # iterates over inputFile and adds to corresponding field in object self
        return None
    
    
        