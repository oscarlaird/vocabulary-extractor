#assemble word frequency data
import os,inspect
path = os.path.split(os.path.abspath(inspect.getfile(inspect.currentframe())))[0] #find abs. path of this addon

def getdata():
    file = open(os.path.join(path,'wordfreqdata.txt'),'r',encoding='utf-8') #800 lines by cB recommended base = 670
    data = []
    for line in file.readlines():
        data.append(line.split('\t'))
    file.close()
    return data