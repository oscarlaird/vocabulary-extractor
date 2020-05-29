# Vocabulary Selector: Base Vocab of 100k words: freq > 4e-7
import re, os, sys, inspect, webbrowser
path = os.path.split(os.path.abspath(inspect.getfile(inspect.currentframe())))[0] #find abs. path of this addon

from aqt import mw
from aqt import gui_hooks
from aqt.qt import *
from PyQt5 import QtCore, QtGui, QtWidgets

from aqt import editor
from anki import notes
from anki.importing import TextImporter

from . import UI #the interface

def checkmodel(arg): #create note type #arg is ignored
    
    model = mw.col.models.byName("Word -> Sentence, Definition")

    if not model:        
        _field_names = ["Word", "Sentence", "Definition"]
        _model_name = "Word -> Sentence, Definition"
        
        mm = mw.col.models
        m = mm.new(_(_model_name))

        for field_name in _field_names:
            fm = mm.newField(_(field_name))
            mm.addField(m, fm)  

        t = mm.newTemplate("Card 1")
        t['qfmt'] = "{{Word}}"
        t['afmt'] = "{{Word}}<hr id=answer>{{Sentence}}<br><br>{{Definition}}"
        mm.addTemplate(m, t)

        mm.add(m)
        mw.col.models.save(m)
def run():
    Interface() #instantiate the Interface
class Interface(QDialog):
    #|----------------------|
    #| [%%%%%%%%%%     ] b1 |
    #|tttttttttttttttttttttt|
    #|                      |
    #|tttttttttttttttttttttt|
    #|tttttttttttttttttttttt|
    #|tttttttttttttttttttttt|
    #|tttttttttttttttttttttt|
    #| b4       b3       b2 |
    #|----------------------|
    
    def __init__(self):
        QDialog.__init__(self,mw)
        self.form = UI.Ui_Form()
        self.form.setupUi(self)
        self.setFixedSize(self.size()) #prevent resizing
        
        self.stage = 1
        self.stage1()
        self.exec_()

    def stage1(self):
        self.stage = 1
        
        #update text
        self.form.bigtext.setText('Welcome to Vocabulary Extractor')
        self.form.smalltext.setText('Please choose a plaintext .txt file from your computer.\nYou can download many classic books in plaintext format at Gutenberg.org.\nDocumentation can be found at https://ankiweb.net/shared/info/1152823001.')
        #update buttons
        self.form.b1.clicked.connect(self.browse); self.bookpath = None
        self.form.b2.clicked.connect(self.next)
        self.form.b3.clicked.connect(self.cancel)
        self.form.b4.clicked.connect(self.help)
        self.form.b1.setText('Browse')
        self.form.b2.setText('Next')
        self.form.b3.setText('Cancel')
        self.form.b4.setText('Help')
    def browse(self):
        self.bookpath = QFileDialog.getOpenFileName(mw,"Choose Book", "", "Text File (*.txt)")[0]
        if not self.bookpath:
            return #do nothing if nothing selected
        self.form.bookbar.setText(self.bookpath)
        self.form.bookbar.setStyleSheet('') #remove red outline if a selection is made
    def next(self):
        if not self.bookpath:
            self.form.bookbar.setStyleSheet("border: 1px solid red")
            return
        self.bookname = os.path.splitext(os.path.basename(self.bookpath))[0] #get bookname
        self.stage2()
    def cancel(self):
        self.close()
    def help(self):
        webbrowser.open('https://ankiweb.net/shared/info/1152823001')

    def stage2(self):
        self.stage = 2
        
        #switch to progressBar
        self.form.stackedWidget.setCurrentIndex(0)
        self.form.progressBar.setValue(0)
        #text
        self.form.bigtext.setText('')
        self.booksize = os.path.getsize(self.bookpath)
        self.estimatedtime = 2*self.booksize/1000000 + 1 #estimated at two minutes per megabyte
        self.form.smalltext.setText('Please wait while the program processes %s.\nIt will take %d minutes to process.\nSteps: compile english dictionary; process book into sentences; find words.'%(self.bookname.upper(),self.estimatedtime))
        #buttons
        self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort); self.aborted = False #reconnect button to abort function
        self.form.b2.hide()
        self.form.b3.hide()
        self.form.b4.hide()
        self.form.b1.setText('Abort')

        self.engdict = compileengdict(self)
        createsbook(self,self.bookpath)
        self.newwords = findnewwords(self,self.engdict)
        
        self.stage3()       
    def abort(self):
        self.aborted = True #findnewwords is the only process that will abort; the rest are fast.
        self.close()

    def stage3(self):
        self.stage = 3
        if not self.newwords: #close if no newwords found.
            QMessageBox.information(mw,'Error','Sorry, no new words were found.')
            self.abort()
        #update text
        self.form.bigtext.setText('')
        self.form.smalltext.setText('Select Learn (press L) if you would like to add this word to your deck. Select Known (press K) if you already know it. \"Learn All\" will add every remaining word to your deck.')
        #update buttons
        self.form.b1.show(); self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort)
        self.form.b2.show(); self.form.b2.clicked.disconnect(); self.form.b2.clicked.connect(self.learn)
        self.form.b3.show(); self.form.b3.clicked.disconnect(); self.form.b3.clicked.connect(self.known)
        self.form.b4.show(); self.form.b4.clicked.disconnect(); self.form.b4.clicked.connect(self.learnall)
        self.form.b1.setText('Abort')
        self.form.b2.setText('Learn')
        self.form.b3.setText('Known')
        self.form.b4.setText('Learn All')
        #word lists
        self.knownwords = []
        self.learnwords = {}
        #begin sorting words
        self.num_words = len(self.newwords)
        self.form.progressBar.setMaximum(self.num_words); self.form.progressBar.setValue(0)
        self.updateWord()
    def keyPressEvent(self,event): #overwrite key handling for L and K hotkeys
        if self.stage == 3:
            if event.key() == Qt.Key_L:
                self.learn()
                return
            if event.key() == Qt.Key_K:
                self.known()
                return
        return QDialog.keyPressEvent(self,event)
    def updateWord(self):
        if not self.newwords:
            self.stage4()
            return
        (self.word,self.sentence) = self.newwords.popitem()
        self.form.bigtext.setText(self.word)
        self.form.smalltext.setText('Select Learn (press L) if you would like to add this word to your deck. Select Known (press K) if you already know it. \"Learn All\" will add every remaining word to your deck.\n\nWord %d / %d'%(len(self.knownwords)+len(self.learnwords)+1,self.num_words))        
        self.form.progressBar.setValue(len(self.knownwords)+len(self.learnwords)+1)
    def learn(self):
        self.learnwords[self.word] = self.sentence
        self.updateWord()
    def known(self):        
        self.knownwords.append(self.word)
        self.updateWord()
    def learnall(self):
        self.learnwords[self.word] = self.sentence
        self.learnwords.update(self.newwords)
        self.newwords = {}
        self.form.progressBar.setMaximum(100); self.form.progressBar.setValue(100)
        self.updateWord()        
    
    def stage4(self):
        self.stage = 4
        
        #text
        self.form.bigtext.setText('Creating Deck')
        self.form.smalltext.setText('Please wait while you deck is created. It will take less than a minute.')
        #buttons
        self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort); self.aborted = False #reconnect button to abort function
        self.form.b2.hide()
        self.form.b3.hide()
        self.form.b4.hide()

        if self.knownwords:
            addknownwords(self.knownwords)
        if self.learnwords: #trying to import a file with no words will raise an error
            writecsv(self.learnwords,self.engdict)
            importdeck(self.bookname)

        self.stage5()
    def stage5(self):
        self.stage = 5
        
        #text
        self.form.bigtext.setText('Deck Creation Successful!')
        self.form.smalltext.setText('')
        #buttons
        self.form.b1.hide()
        self.form.b3.show(); self.form.b3.clicked.disconnect(); self.form.b3.clicked.connect(self.abort); self.form.b3.setText('Close') #close dialog     

def compileengdict(ui): #read engdict.txt into engdict
    ui.form.bigtext.setText('Compiling English Dictionary')
    progress = 0; dictsize = os.path.getsize(os.path.join(path, 'engdict.txt')); prevupdate = 0 #progress towards finishing
    ui.form.progressBar.setMaximum(dictsize)
    
    engdictraw = open(os.path.join(path, 'engdict.txt'),'r',encoding='utf-8') #sourced from http://www.mso.anu.edu.au/~ralph/OPTED/
    prevword = ''; engdict = {}
    for line in engdictraw:
        (word,defn) = line.split(' ',1)
        
        if defn[0] != '(': defn = '~ ' + defn #multiword definitions
        
        if word in engdict.keys():
            engdict[word] = engdict[word] + ' ' + defn[:-1]
        else:
            prevword = word
            engdict[word] = defn[:-1]
         
        #update the interface
        progress += len(line)+1
        if progress > prevupdate + 100000:
            ui.form.progressBar.setValue(progress)
            prevupdate = progress
  
    engdictraw.close()
    return engdict #return an english dictionary
def createsbook(ui,bookpath): #process book into sentence lines (sbook)
    ui.form.bigtext.setText('Processing Book into Sentences')
    progress = 0; booksize = os.path.getsize(bookpath); prevupdate = 0 #progress towards finishing
    ui.form.progressBar.setMaximum(booksize)
    
    book = open(bookpath,'r',encoding='utf-8')
    sbook = open(os.path.join(path, 'sbook.txt'),'w',encoding='utf-8')
    for line in book:
        sbook.write(re.sub('([.!?][\'\"”’]?)\s*','\\1\n',line[:-1]+' ')) #remove newlines then establish newlines at .?!"
        #update the interface
        progress += len(line)+1
        if progress > prevupdate + 1000: #update every 10 kilobytes
            ui.form.progressBar.setValue(progress)
            prevupdate = progress

    sbook.close()
    book.close()
def getlemmas(word): #get lemmas from a word
    word=word.lower()
    lemmas = [word,]

    prefix2 = word[:2] #prefixes
    prefix3 = word[:3]
    if prefix2 in ['re','un','in','im','dis']:
        lemmas.extend(getlemmas(word[2:]))
    elif prefix3 == 'dis':
        lemmas.extend(getlemmas(word[3:]))
        
    suffix1 = word[-1:] #suffixes
    suffix2 = word[-2:]    
    suffix3 = word[-3:]
    suffix4 = word[-4:]        
    suffix5 = word[-5:]
    if suffix5 in ['iness','iment','iless']: #5
        lemmas.extend(getlemmas(word[:-5]+'y'))
    elif suffix5=='ility':
        lemmas.extend(getlemmas(word[:-5]+'le'))
    if suffix4 in ['ness','ment','like','less']: #4
        lemmas.extend(getlemmas(word[:-4]))
    elif suffix4=='able':
        lemmas.extend(getlemmas(word[:-4]))
        lemmas.extend(getlemmas(word[:-4]+'e'))
    elif suffix4 in ['iful','iest']:
        lemmas.extend(getlemmas(word[:-4]+'y'))
    if suffix3=='ing': #3
        lemmas.extend(getlemmas(word[:-3]))
        lemmas.extend(getlemmas(word[:-3]+'e'))
    if suffix3 in ['ful','ist','est']:
        lemmas.extend(getlemmas(word[:-3]))
    elif suffix3=='ily':
        lemmas.extend(getlemmas(word[:-3]+'y'))
    if suffix2 in ['es','al']: #2
        lemmas.extend(getlemmas(word[:-2]))
    elif suffix2 in ['ly','ed','er']:
        lemmas.extend(getlemmas(word[:-2]))
        lemmas.extend(getlemmas(word[:-2]+'e'))
    if suffix1=='s': #1
        lemmas.extend(getlemmas(word[:-1]))
        
    return sorted(lemmas,key=len) #return lemmas (no duplicates)
def findnewwords(ui,engdict): #find newwords in sbook
    ui.form.bigtext.setText('Finding Words')
    sbook = open(os.path.join(path, 'sbook.txt'),'r',encoding='utf-8')
    basevocabobj = open(os.path.join(path, 'BaseVocab.txt'),'r',encoding='utf-8'); basevocab = basevocabobj.read().split(); basevocabobj.close()
    uservocabobj = open(os.path.join(path, 'UserVocab.txt'),'r+',encoding='utf-8'); uservocab = uservocabobj.read().split(); uservocabobj.close()
    progress = 0; booksize = os.path.getsize(os.path.join(path, 'sbook.txt')); prevupdate = 0 #progress towards finishing
    ui.form.progressBar.setMaximum(booksize)

    newwords = {}
    for sentence in sbook:
        for word in re.split('[0-9%*,.!?;—():/“”’\-\'\"\s]+',sentence): # Break the line into words:
            word = word.lower()
            lemmas = getlemmas(word)
            for lemma in lemmas:
                if (lemma in basevocab) or (lemma in uservocab) or (lemma in newwords):
                    break #break if any lemma already known
            else:
                for lemma in lemmas:
                    if lemma in engdict.keys():
                        #choose the lemma with the longest definition
                        bestdictlemma = max([lemma for lemma in lemmas if lemma in engdict.keys()],key=(lambda lemma: len(engdict[lemma])))
                        newwords[bestdictlemma] = sentence #add word:sentence pair to newwords
                        break
        #update the interface
        progress += len(sentence)+1 #chars = #bytes for progress
        if progress > prevupdate + 1000:
            QCoreApplication.processEvents()
            ui.form.progressBar.setValue(progress)
            prevupdate = progress
            if ui.aborted == True: #check whether to abort
                break
    sbook.close()
    return newwords #return newwords dictionary
def sortwords(newwords): #ask the user whether they want to learn each word
    progressMsg.close()

    knownwords = []
    learnwords = {}
    
    num_words = len(newwords)
    while True:
        try:
            (word,sentence) = newwords.itempop()
            mw.msgBox = msgBox = QMessageBox()
            kb = msgBox.addButton("&Known", QMessageBox.ActionRole)
            lb = msgBox.addButton("&Learn", QMessageBox.ActionRole)
            ab = msgBox.addButton("Learn &All", QMessageBox.ActionRole)
            msgBox.setText("%s"%word) #word
            msgBox.setInformativeText('Known (press k) if you know this.\nLearn (press l) to put in your deck.\nProgress %i / %i'%(len(newwords),num_words))
            msgBox.setWindowTitle("Word %i / %i"%(len(newwords),num_words)) #progress
            msgBox.exec()

            if (msgBox.clickedButton() == kb):
                knownwords.append(word)
            elif (msgBox.clickedButton() == lb):
                learnwords[word]=sentence #copy dictionary entry
            elif (msgBox.clickedButton() == ab):
                learnwords[word]=sentence
                learnwords.update(newwords)
                break
        except KeyError:
            break

    #return knownwords,learnwords
    return (knownwords,learnwords)
def addknownwords(knownwords): #add knownwords to permanent uservocab
    uservocabobj = open(os.path.join(path, "UserVocab.txt"),'r+',encoding='utf-8')
    for word in knownwords:
        uservocabobj.write('\n'+word)
    uservocabobj.close()
def writecsv(learnwords,engdict): #create ankideck csv from learnwords
    ankideck = open(os.path.join(path, "ankideck.txt"),'w',encoding='utf-8')
    for word in learnwords.keys():
        ankideck.write(word + '\t' + learnwords[word][:-1] + '\t' + engdict[word] + '\n')
    ankideck.close()
def importdeck(bookname): #import deck into anki
    csv = os.path.join(path, 'ankideck.txt')
    # select deck
    did = mw.col.decks.id(bookname)
    mw.col.decks.select(did)
    # assign right model to deck
    m = mw.col.models.byName("Word -> Sentence, Definition")
    mid = m['id'] 
    deck = mw.col.decks.get(did)
    deck['mid'] = m['id']
    mw.col.decks.save(deck)
    # assign right deck to model
    m['did'] = did
    # import into the collection
    ti = TextImporter(mw.col, csv)
    ti.initMapping()
    ti.run()
    #refresh to show deck
    mw.deckBrowser.refresh()

#menu item triggers program
action = QAction("Extract Vocabulary from Book...", mw)
action.triggered.connect(run)
mw.form.menuTools.addAction(action)
#check for note type on load
gui_hooks.collection_did_load.append(checkmodel) #after collection loads create note type if it doesn't yet exist.
