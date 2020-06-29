import os
import requests
from bs4 import BeautifulSoup

path = os.path.abspath(os.path.dirname(__file__))

querried = True

def load_dictionary():
    pass
    
def querry_word(word):
    source = requests.get(f'https://www.lexico.com/definition/{word}').text
    
    soup = BeautifulSoup(source, 'lxml') #use the fastest (lxml) parser
    etym = soup.find("section",class_="etymology etym").find("p").get_text()
    defns = [defn.get_text() for gramb in soup.find_all("section",class_="gramb") for defn in gramb.find_all("span", class_="ind")]
    
    if etym
        defns += '(etymology) '+etym
    
    return defns
