#get possible lemmas using naive stemming
import re

def getlemmas(word): #get lemmas from a word
    word=word.lower()
    lemmas = [word,]

    prefix2 = word[:2] #prefixes
    prefix3 = word[:3]
    if prefix2 in ['re','un','in','im']:
        lemmas.extend(getlemmas(word[2:])) #run function again with prefix removed
    elif prefix3 in ['dis','non','mis']:
        lemmas.extend(getlemmas(word[3:]))
        
    suffix1 = word[-1:] #suffixes
    suffix2 = word[-2:]    
    suffix3 = word[-3:]
    suffix4 = word[-4:]        
    suffix5 = word[-5:]
    if re.match('([a-z])\1(ing|est)',suffix5):
        lemmas.append(word[:-4]) #Get the root verb of a gerund or superlative with a doubled letter.
    elif suffix5 in ['iness','iment','iless']: #5
        lemmas.append(word[:-5]+'y')
    elif suffix5=='ility':
        lemmas.append(word[:-5]+'le')
    elif suffix5=='ation':
        lemmas.append(word[:-5]+'')
        lemmas.append(word[:-5]+'e')
        lemmas.append(word[:-5]+'ate')
        
    if re.match('([a-z])\1(ed|er)',suffix5):
        lemmas.append(word[:-3]) #Get the root verb of a past tense or comparative with a doubled letter.
    elif suffix4 in ['ness','ment','like','less']: #4
        lemmas.append(word[:-4])
    elif suffix4=='able':
        lemmas.append(word[:-4])
        lemmas.append(word[:-4]+'e')
    elif suffix4 in ['iful','iest']:
        lemmas.append(word[:-4]+'y')
    elif suffix4 == 'ency':
        lemmas.append(word[:-4]+'ent') #e.g. clemency
    elif suffix4 == 'ancy':
        lemmas.append(word[:-4]+'ant') #e.g. relevancy
        
    if suffix3=='ing': #3
        lemmas.append(word[:-3])
        lemmas.append(word[:-3]+'e')
    if suffix3 in ['ful','ist','est','ity']:
        lemmas.append(word[:-3])
    if suffix3 == 'men':
        lemmas.append(word[:-3]+'man')
    elif suffix3=='ily':
        lemmas.append(word[:-3]+'y')
    
    if suffix2 in ['es','al']: #2
        lemmas.append(word[:-2])
    elif suffix2 in ['ly','ed','er']:
        lemmas.append(word[:-2])
        lemmas.append(word[:-2]+'e')
        if suffix2 == 'ly':
            lemmas.append(word[:-2]+'le')
    if suffix1 in ['s','y']: #1
        lemmas.append(word[:-1]) #e.g. soldiers or soldiery
        
    return sorted(lemmas,key=len) #return lemmas (no duplicates) #sort by length because loop breaks on finding first known lemma