import timeit
import re
files = []
def test1():
    header = []
    with open('12506001.p2019', 'r', encoding="utf8", errors='ignore') as td:
        for line in td:
            if re.match('-- DATA --', line): # end-of-header            
                return header
            else:
                header.append(line)
            

def time1():

    start = timeit.timeit()
    header = test1()
    stop = timeit.timeit()
    print(header)
    return stop-start

def test2():
    header = []
    with open('12506001.p2019', 'r', encoding="utf8", errors='ignore') as td:
        line = td.readline()
        if '-- DATA --' in line:
            return header
        else:
            header.append(line)
            print(line)

def time2():
    start = timeit.timeit()
    header = test2()
    stop = timeit.timeit()
    print(header)
    return stop-start
