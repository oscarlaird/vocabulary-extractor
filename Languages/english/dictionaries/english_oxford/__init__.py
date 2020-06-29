import os
import requests
from bs4 import BeautifulSoup
import time

path = os.path.abspath(os.path.dirname(__file__))

querried = True

def load_dictionary():
    pass
    
def querry_word(word):
    source = requests.get(f'https://www.lexico.com/definition/{word}').text #Lexico limits us to 1 request / 3s
    
    soup = BeautifulSoup(source, 'html.parser') #use the fastest (lxml) parser        
    try:
        defns = [defn.get_text() for gramb in soup.find_all("section",class_="gramb") for defn in gramb.find_all("span", class_="ind")]
    except:
        return
        
    try:
        etym = soup.find("section",class_="etymology etym").find("p").get_text()
    except:
        etym = False
    
    if etym:
        defns += '(etymology) '+etym
    
    time.sleep(3) #wait three seconds before continuing -- lexico.com limits requests
    
    return defns
