import os
import requests
import re
path = os.path.abspath(os.path.dirname(__file__))

querried = True

def load_dictionary():
    pass
    
def querry_word(word):
    source = requests.get('https://www.lexico.com/definition/cotillion').text
    defns = re.findall('<span class="ind">[^<]+</span>',source)
    defns = [defn[18:-7] for defn in defns]
    return defns
    
print(querry_word('word'))