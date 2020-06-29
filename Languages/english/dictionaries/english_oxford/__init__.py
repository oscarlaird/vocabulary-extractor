import os
import requests
import re
path = os.path.abspath(os.path.dirname(__file__))

querried = True

def load_dictionary():
    pass
    
def querry_word(word):
    source = requests.get(f'https://www.lexico.com/definition/{word}').text
    defns = re.findall('<span class="ind">[^<]+</span>',source)
    defns = [defn[18:-7] for defn in defns]
    origin = re.search('class="senseInnerWrapper"><p>([^<]+)<',source)
    if origin:
        defns += [origin.group(1)]
    return defns
