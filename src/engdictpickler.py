#pickle engdict

import os
import pickle
path = os.path.abspath(os.path.dirname(__file__)) #find abs. path of this module

def compileengdict():
    #Create and English Dictionary: Each entry is a list of definitions.
    
    engdictraw = open(os.path.join(path, 'engdict.txt'),'r',encoding='utf-8') #sourced from http://www.mso.anu.edu.au/~ralph/OPTED/
    prevword = ''; engdict = {}
    for line in engdictraw:
        (word,defn) = line.split(' ',1); defn = defn[:-1] #get word and definition #without newline  
        if defn[0] != '(': defn = '~ ' + defn #multiword definitions
        
        if word == prevword:
            engdict[word].append(defn)
        else:
            engdict[word] = [defn]
            prevword = word
  
    engdictraw.close()
    return engdict #return an english dictionary
    
def createdict():
    file = open(os.path.join(path, 'engdict.pickle'),'wb')
    pickle.dump(compileengdict(),file)
    file.close()
    
def opendict():
    #Create the file if it does not yet exist.
    try:
        file = open(os.path.join(path, 'engdict.pickle'),'rb')
    except FileNotFoundError:
        createdict()
        file = open(os.path.join(path, 'engdict.pickle'),'rb')
    #load and return the dictionary
    engdict = pickle.load(file)
    file.close()
    return engdict