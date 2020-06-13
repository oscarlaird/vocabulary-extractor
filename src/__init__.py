# Vocabulary Extractor #June 2020
# Word list from wordfreq python module #possibly SCOWL would be a superior alternative
# English Ditionary sourced from a public domain 1913 Merriam Webster Dictionary

#IMPORTS
#System
import re, os, platform, webbrowser
from shutil import copyfile

#Qt
from aqt import mw
from aqt import gui_hooks
from aqt.qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
from aqt.reviewer import Reviewer #the review page is a QWebEnginePage
#Anki
from anki import notes
from anki.importing import TextImporter
#Add-on (internal)
from . import wordfreq
from .getlemmas import getlemmas
from . import levenshtein
from . import ui
from . import shortcutsUI
from . import engdictpickler

#Variables
path = os.path.abspath(os.path.dirname(__file__)) #find abs. path of this addon
mac = (platform.system() == 'Darwin') #macOS requires flushing qt events by repainting
config = mw.addonManager.getConfig(__name__) #User's options
engdict = {}
highlight_action = None; redefine_action = None
#Setup
def setup(arg): #load dictionary, create note type #arg is ignored

    #Load English Dictionary
    global engdict #Dictionary must be global so that it may be loaded once and accessed both by the extractor and the reviwer
    engdict = engdictpickler.opendict()
    
    #Make Menu
    makeMenu()
    #Hooks
    gui_hooks.state_did_revert.append(onRevert) #show answer immediately if undo highlight or redefine  
    #MODEL is anki's word for note type TEMPLATE is anki's word for card type
    model = mw.col.models.byName("Excerpt Vocabulary") #Get the Model
    if not model: #Create the Model if it doesn't exist yet.
        _field_names = ["Word", "Sentence", "Definition","(WF)","(SF)"]
        _model_name = "Excerpt Vocabulary"
        
        mm = mw.col.models #get the model manager
        m = mm.new(_(_model_name))

        for field_name in _field_names:
            fm = mm.newField(_(field_name))
            mm.addField(m, fm)  
        
        if 'new_template' in dir(mm):
            t = mm.new_template("WF")
        else:
            t = mm.newTemplate("WF") #legacy support
        t['qfmt'] = "{{#(WF)}}{{Word}}{{/(WF)}}"
        t['afmt'] = "{{Word}}<hr>{{Sentence}}<hr><p align=left>{{Definition}}</p>"
        if 'add_template' in dir(mm):
            mm.add_template(m, t)
        else:
            mm.addTemplate(m, t) #legacy support
        
        if 'new_template' in dir(mm):
            t2 = mm.new_template("SF")
        else:
            t2 = mm.newTemplate("SF") #legacy support
        t2['qfmt'] = "{{#(SF)}}{{Sentence}}{{/(SF)}}"
        t2['afmt'] = "{{Sentence}}<hr><p align=left>{{Definition}}</p>"
        if 'add_template' in dir(mm):
            mm.add_template(m, t2)
        else:
            mm.addTemplate(m, t2) #legacy support

        mm.add(m)
        mw.col.models.save(m)
    if model: #Update the Model #This is necessary so that I can make changes to the model for existing users
        for template in model["tmpls"]:
            if template['name']=='WF':
                template['qfmt'] = "{{#(WF)}}{{Word}}{{/(WF)}}"
                template['afmt'] = "{{Word}}<hr>{{Sentence}}<hr><p align=left>{{Definition}}</p>"
            elif template['name']=='SF':
                template['qfmt'] = "{{#(SF)}}{{Sentence}}{{/(SF)}}"
                template['afmt'] = "{{Sentence}}<hr><p align=left>{{Definition}}</p>"
        mw.col.models.save(model)
def makeMenu():
    global highlight_action, redefine_action
    #VE Sub-menu
    VE_menu = mw.form.menuTools.addMenu("Vocabulary Extractor")
    #Main VE Dialog
    VE_launch = QAction("EXTRACT...", mw)
    VE_launch.triggered.connect(run)
    VE_menu.addAction(VE_launch)
    #Shortcuts
    #Shortcuts Dialog
    Set_Shortcuts_launch = QAction("Set Shortcuts", mw)
    Set_Shortcuts_launch.triggered.connect(setShortcuts)
    VE_menu.addAction(Set_Shortcuts_launch)
    #Load Shortcut Sequences
    highlight_shortcut = QKeySequence.fromString(config["highlight_shortcut"])
    redefine_shortcut = QKeySequence.fromString(config["redefine_shortcut"])
    #Create Definition Shortcuts
    highlight_action = VE_menu.addAction("Highlight",highlight,highlight_shortcut)    
    redefine_action = VE_menu.addAction("Redefine",redefine,redefine_shortcut)
gui_hooks.collection_did_load.append(setup)
#Deck Creation Dialog 
class Interface(QDialog):
    
    def __init__(self):
        QDialog.__init__(self,mw)
        self.form = ui.Ui_Form()
        self.form.setupUi(self)
        self.setWindowTitle('Vocabulary Extractor')
        self.form.bigtext.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.stage = 1; self.stage1()
        
        self.exec_()

    def stage1(self): #OPTIONS
        self.stage = 1
        
        #Set Level
        self.level = config["level"]
        self.form.levelselector.setValue(self.level - 630)
        #use correct bg color for smalltext
        self.setbg()
        #update text
        self.form.wordprogress.setText('')
        self.form.bigtext.setText('Select Book')
        #update radio buttons from configuration
        self.excerptType = config["excerpt_type"]
        self.cardType = config["card_type"]
        if self.excerptType == 'Sentences':
            self.form.sentencesrb.setChecked(True)
        elif self.excerptType == 'Semicolons':
            self.form.semicolonsrb.setChecked(True)
        elif self.excerptType == 'Lines':
            self.form.linesrb.setChecked(True)
        if self.cardType == 'WF':
            self.form.wordfrontrb.setChecked(True)
        if self.cardType == 'SF':
            self.form.sentencefrontrb.setChecked(True)
        if self.cardType == 'Both':
            self.form.bothrb.setChecked(True)
        #update buttons
        self.form.b1.clicked.connect(self.browse); self.bookpath = None
        self.form.b2.clicked.connect(self.next)
        self.form.b3.clicked.connect(self.cancel)
        self.form.b4.clicked.connect(self.help)
        self.form.b1.setText('Browse')
        self.form.b2.setText('Next')
        self.form.b3.setText('Cancel')
        self.form.b4.setText('Help')
        
        self.form.b1.setAutoDefault(False); self.form.b1.setDefault(False)
        self.form.b2.setAutoDefault(False); self.form.b2.setDefault(False)
        self.form.b3.setAutoDefault(False); self.form.b3.setDefault(False)
        self.form.b4.setAutoDefault(False); self.form.b4.setDefault(False)
        
        
        self.form.b1.setDefault(True) #browse by default        
    def browse(self):
        browse_path = config["browse_path"]
        if browse_path == 'Examples':
            browse_path = os.path.join(path,'Examples')
        self.bookpath = QFileDialog.getOpenFileName(mw,"Choose Book", browse_path, "Text File (*.txt)")[0]
        if not self.bookpath:
            return #do nothing if nothing selected
        self.form.bookbar.setText(self.bookpath)
        self.form.bookbar.setStyleSheet('') #remove red outline if a selection is made
        self.form.b1.setDefault(False); self.form.b2.setDefault(True) #next by default
    def next(self):
        if not self.bookpath:
            self.form.bookbar.setStyleSheet("border: 1px solid red")
            return
        self.retrieveOptions()
        self.stage2()
    def cancel(self):
        self.close()
    def help(self):
        webbrowser.open('https://ankiweb.net/shared/info/1152823001') #open ANKI documentation
    def setbg(self):
        bg = self.palette().color(self.backgroundRole()) #background color is platform dependent
        p = self.form.smalltext.viewport().palette()
        p.setColor(self.form.smalltext.viewport().backgroundRole(), bg)
        self.form.smalltext.viewport().setPalette(p) #set smalltext to have a gray background
    def retrieveOptions(self):
        self.level = 630 + self.form.levelselector.value()
        config["level"] = self.level
        
        if self.form.sentencesrb.isChecked():
            self.excerptType = 'Sentences'
        if self.form.semicolonsrb.isChecked():
            self.excerptType = 'Semicolons'
        if self.form.linesrb.isChecked():
            self.excerptType = 'Lines'
        config["excerpt_type"] = self.excerptType
        
        if self.form.wordfrontrb.isChecked():
            self.wordcards = 'yes'
            self.sentencecards = '' #Anki will condition on whether this field is empty
            config["card_type"] = "WF"
        if self.form.sentencefrontrb.isChecked():
            self.wordcards = ''
            self.sentencecards = 'yes'
            config["card_type"] = "SF"
        if self.form.bothrb.isChecked():
            self.wordcards = 'yes'
            self.sentencecards = 'yes'
            config["card_type"] = "Both"
        
        config["browse_path"] = os.path.split(self.bookpath)[0]
        
        mw.addonManager.writeConfig(__name__, config) #save options
        
        self.bookname = os.path.splitext(os.path.basename(self.bookpath))[0] #get bookname

    def stage2(self): #PROCESSING
        self.stage = 2
        
        #switch to progressBar #switch to smalltext
        self.form.stackedWidget.setCurrentIndex(0)
        self.form.progressBar.setValue(0)
        self.form.stackedWidget_2.setCurrentIndex(0)
        #text
        self.form.bigtext.setText('')
        self.booksize = os.path.getsize(self.bookpath)
        self.estimatedtime = 2*self.booksize/1000000 + 1 #estimated at two minutes per megabyte
        self.form.smalltext.setText('Please wait while the program processes %s.\nIt will take %d minutes to process.\n\nIn Sorting Step:\nPress K to mark as known.\nPress L to learn.\n\nDuring Review:\nPress %s to use a definition of the selected word instead.\nPress %s to highlight the selected text.'%(self.bookname.upper(),self.estimatedtime,config["redefine_shortcut"],config["highlight_shortcut"]))
        #buttons
        self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort); self.aborted = False #reconnect button to abort function
        self.form.b2.hide()
        self.form.b3.hide()
        self.form.b4.hide()
        self.form.b1.setText('Abort')

        self.engdict = engdict
        createsbook(self,self.bookpath,self.excerptType)
        self.newwords = findnewwords(self,self.engdict,self.level)
        
        self.stage3()       
    def abort(self):
        self.aborted = True #findnewwords is the only process that will checks for abort.
        self.close()

    def stage3(self): #SORTING
        self.stage = 3
        if not self.newwords: #close if no newwords found.
            QMessageBox.information(mw,'Error','Sorry, no new words were found.')
            self.abort()
        #update text
        self.form.bigtext.setText('')
        #update buttons
        self.form.b1.show(); self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort)
        self.form.b2.show(); self.form.b2.clicked.disconnect(); self.form.b2.clicked.connect(self.learn)
        self.form.b3.show(); self.form.b3.clicked.disconnect(); self.form.b3.clicked.connect(self.known)
        self.form.b4.show(); self.form.b4.clicked.disconnect(); self.form.b4.clicked.connect(self.learnall)
        self.form.b1.setText('Abort')
        self.form.b2.setText('Learn (l)')
        self.form.b3.setText('Known (k)')
        self.form.b4.setText('Learn All')
        #word lists
        self.learnwords = [] #list of triples: word, sentence, definition
        #begin sorting words
        self.word_num = 1 #counter to track progress
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
        return QDialog.keyPressEvent(self,event) #handle other keys normally     
    def updateWord(self):
        if not self.newwords:
            self.stage4()
            return
        triple = self.newwords.pop(0)
        (self.word,self.sentence,self.definition) = triple
        self.form.bigtext.setText(self.word)
        self.form.smalltext.setText(self.qbackside(triple))
        
        #progress
        self.form.wordprogress.setText('%i / %i'%(self.word_num,self.num_words))
        self.form.progressBar.setValue(self.word_num)
        if mac: self.repaint()  # flush events
    def qbackside(self,triple):
        (word,sentence,definition) = triple
        return '<span>' + self.sentence.replace(self.word,'</span><span style="background-color:yellow"><b>'+self.word+'</b></span><span>').replace(self.word.capitalize(),'</span><span style="background-color:yellow"><b>'+self.word.capitalize()+'</b></span><span>') + '</span>'
    def learn(self):
        self.learnwords.append([self.word,self.sentence,self.definition])
        self.word_num += 1
        self.updateWord()
    def known(self):        
        self.word_num += 1
        self.updateWord()
    def learnall(self):
        self.learnwords.append([self.word,self.sentence,self.definition])
        self.learnwords.extend(self.newwords)
        self.newwords = []
        self.form.progressBar.setMaximum(100); self.form.progressBar.setValue(100)
        self.updateWord()        
    
    def stage4(self):
        self.stage = 4
        
        #text
        self.form.wordprogress.setText('')
        self.form.bigtext.setText('Creating Deck')
        self.form.smalltext.setText('Please wait while you deck is created. It will take less than a minute.')
        #buttons
        self.form.b1.clicked.disconnect(); self.form.b1.clicked.connect(self.abort); self.aborted = False #reconnect button to abort function
        self.form.b2.hide()
        self.form.b3.hide()
        self.form.b4.hide()
        if mac: self.repaint()

        if self.learnwords: #trying to import a file with no words will raise an error
            writecsv(self.learnwords,self.engdict,self.wordcards,self.sentencecards)
            importdeck(self.bookname)

        self.stage5()
    def stage5(self):
        self.stage = 5
        
        #text
        self.form.bigtext.setText('Deck Creation Successful!')
        self.form.smalltext.setText('During Review:\nPress %s to use a definition of the selected word instead.\nPress %s to highlight the selected text.'%(config["redefine_shortcut"],config["highlight_shortcut"]))
        #buttons
        self.form.b1.hide()
        self.form.b3.show(); self.form.b3.clicked.disconnect(); self.form.b3.clicked.connect(self.abort); self.form.b3.setText('Close') #close dialog     
def run():
    Interface() #instantiate the Interface which handles the rest
def createsbook(ui,bookpath,excerptType): #process book into sentence lines (sbook)
    if excerptType == 'Lines':
        copyfile(bookpath,os.path.join(path, 'sbook.txt')) #use source text
        return
    elif excerptType == 'Sentences':
        delimiters = '.?!'
    elif excerptType == 'Semicolons':
        delimiters = '.?!;'

    ui.form.bigtext.setText('Processing Book into Sentences')
    progress = 0; booksize = os.path.getsize(bookpath); prevupdate = 0 #progress towards finishing
    ui.form.progressBar.setMaximum(booksize)

    book = open(bookpath,'r',encoding='utf-8')
    sbook = open(os.path.join(path, 'sbook.txt'),'w',encoding='utf-8')
    for line in book:
        sbook.write(re.sub('(['+delimiters+'][\'\"”’]?)\s*','\\1\n',line[:-1]+' ')) #remove newlines then establish newlines at .?!"
        #update the interface
        progress += len(line)+1
        if progress > prevupdate + 1000: #update every 10 kilobytes
            ui.form.progressBar.setValue(progress)
            prevupdate = progress

    sbook.close()
    book.close()
def findnewwords(ui,engdict,level): #find newwords in sbook
    ui.form.bigtext.setText('Finding Words')
    sbook = open(os.path.join(path, 'sbook.txt'),'r',encoding='utf-8')
    freqlist = wordfreq.getdata()
    basevocab = [word for line in freqlist[:level] for word in line] #basevocab is a subset of freq list (up to level)
    progress = 0; booksize = os.path.getsize(os.path.join(path, 'sbook.txt')); prevupdate = 0 #progress towards finishing
    ui.form.progressBar.setMaximum(booksize)

    newwords = []
    newforms = []
    for sentence in sbook:
        sentence = sentence.strip() #remove newline
        for word in re.split('[0-9%*,.!?;—():/“”’\-\'\"\s]+',sentence): # Break the line into words:
            word = word.lower()
            lemmas = getlemmas(word)
            for lemma in lemmas:
                if (lemma in basevocab) or (lemma in newforms):
                    break #break if any lemma already known
            else:
                bestdef = getbestdef(word,sentence,lemmas,basevocab)
                if bestdef:
                    newwords.append([word,sentence,bestdef])
                    newforms += lemmas #add these lemmas so they will not get flagged again.
        #update the interface
        progress += len(sentence)+1 #chars = #bytes for progress
        if progress > prevupdate + 1000:
            QCoreApplication.processEvents()
            ui.form.progressBar.setValue(progress)
            prevupdate = progress
            if ui.aborted == True: #check whether to abort
                break
    sbook.close()
    return newwords #return newwords triples: word, sentence, defn
def writecsv(learnwords,engdict,wf,sf): #create ankideck csv from learnwords #wf and sf specify which card types to make
    ankideck = open(os.path.join(path, "ankideck.txt"),'w',encoding='utf-8')
    for triple in learnwords:
        #triplecsv = [s.replace(';',':') for s in triple] #replace semicolons which disrupt importation
        (word, sentence, definition) = triple
        sentence,definition = sentence.replace('\"','\''),definition.replace('\"','\'') #IMPORTANT: without this line doublequotes will disturb the csv import
        sentence = sentence.replace(word,'<mark><b>' + word + '</b></mark>').replace(word.capitalize(),'<mark><b>' + word.capitalize() + '</b></mark>').replace(word.upper(),'<mark><b>' + word.upper() + '</b></mark>') #highlight the word in the sentence
        fields = [word, sentence, definition, wf, sf]
        ankideck.write('\t'.join(fields)+'\n')
    ankideck.close()
def importdeck(bookname): #import deck into anki
    csv = os.path.join(path, 'ankideck.txt')
    # select deck
    did = mw.col.decks.id(bookname)
    mw.col.decks.select(did)
    # assign right model to deck
    m = mw.col.models.byName("Excerpt Vocabulary")
    mid = m['id'] 
    deck = mw.col.decks.get(did)
    deck['mid'] = m['id']
    mw.col.decks.save(deck)
    # assign right deck to model
    m['did'] = did
    # import into the collection
    ti = TextImporter(mw.col, csv)
    ti.patterns = '\t'
    ti.delimiter = '\t' #Force Anki to use tab as delimiter #default = auto-detected delimiter which sometimes causes caatstrophic failure
    ti.allowHTML = True #allow for bold and mark tags
    ti.initMapping()
    ti.run()
    #refresh to show deck
    mw.deckBrowser.refresh()
def getbestdef(word,sentence,lemmas,basevocab):
    def get_variants(lemmas):
        variants = []
        for lemma in lemmas:
            for defn in engdict.get(lemma,[]):
                #regex: (POS)(Reference Preposition)(Word)(Stop)
                referred = re.search('(\(.*?\))( Of | | See | A | Alt. of | Of or pertaining to | Of or pertaining to the )([a-zA-Z]+)([.;])', defn)
                if referred:
                    variant = referred.group(3).lower()
                    if levenshtein.ratio(lemma,variant,truncate=True)>0.80: #Only use referred variants which are somewhat similar. Truncate to compare stems.
                        variants.append(variant)
                #regex: (POS)(---)(Reference Preposition)(Word)
                referredpos = re.search('(\(.*?\))(.*?)(imp. of |p. p. of |vb. n. of |pl. of |sing. of )([a-zA-Z]+)', defn)
                if referredpos:
                    variants.append(referredpos.group(4).lower())
                #regex (POS)(---)(See)(Word)
                seereferred = re.search('(\(.*?\))(.*?)(See )([a-zA-Z]+)', defn)
                if seereferred:
                    variant = seereferred.group(4).lower()
                    if levenshtein.ratio(lemma,variant,truncate=True)>0.80: #Only use referred variants which are somewhat similar. Truncate to compare stems.
                        variants.append(variant)
        return variants
    if set(lemmas).isdisjoint(engdict.keys()): #no lemmas are in the dictionary
        return False
    variants = get_variants(lemmas)
    if not set(variants).isdisjoint(basevocab): #a variant spelling is in the user's vocabulary
        return False
    
    bestform,bestdef = max([(form,'<br>'.join(engdict.get(form,[]))) for form in lemmas+variants],key=lambda pair: len(pair[1]))
    worddef = '<br>'.join(engdict.get(word,[]))
    if worddef and word != bestform:
        return worddef + '<br><br>' + bestform.capitalize() + '<br>' + bestdef
    else:
        return bestform.capitalize() + '<br>' + bestdef    
#Shortcuts
class shortcutsInterface(QDialog):    
    def __init__(self):
        QDialog.__init__(self,mw)
        self.form = shortcutsUI.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle('Set Shortcuts')
        
        #Get existing shortcuts
        self.highlight_shortcut = QKeySequence.fromString(config["highlight_shortcut"])
        self.redefine_shortcut = QKeySequence.fromString(config["redefine_shortcut"])
        #Show existing shortcuts
        self.form.highlightShortcutEdit.setKeySequence(self.highlight_shortcut)
        self.form.redefineShortcutEdit.setKeySequence(self.redefine_shortcut)
        #Explaine Shortcuts
        self.setExplanation()
        #Update Exaplanation when Shortcuts are chosen
        self.form.highlightShortcutEdit.keySequenceChanged.connect(self.updateExplanation)
        self.form.highlightShortcutEdit.keySequenceChanged.connect(self.updateExplanation)
        #Open Dialog
        self.accepted.connect(self.saveShortcuts)          
        self.exec_()
    
    def setExplanation(self):
        #Explain shortcuts to the user
        self.form.highlightShortcutLabel.setText('Highlight Shortcut: Press %s to highlight the selected text.'%self.highlight_shortcut.toString())
        self.form.redefineShortcutLabel.setText('Redefine Shortcut: Press %s to use a definition of the selected word instead.'%self.redefine_shortcut.toString())
    def updateExplanation(self):
        self.highlight_shortcut = self.form.highlightShortcutEdit.keySequence()
        self.redefine_shortcut = self.form.redefineShortcutEdit.keySequence()
        self.setExplanation()
    def saveShortcuts(self):
        config["highlight_shortcut"] = self.form.highlightShortcutEdit.keySequence().toString()
        config["redefine_shortcut"] = self.form.redefineShortcutEdit.keySequence().toString()
        mw.addonManager.writeConfig(__name__, config) #update JSON configuration

        updateShortcuts() #update the shortcuts
def setShortcuts():
    shortcutsInterface()
def updateShortcuts():
    global highlight_action, redefine_action
    highlight_shortcut = QKeySequence.fromString(config["highlight_shortcut"])
    redefine_shortcut = QKeySequence.fromString(config["redefine_shortcut"])

    highlight_action.setShortcut(highlight_shortcut)
    redefine_action.setShortcut(redefine_shortcut)
#Redefine and Highlight during Review
def redefine():
    card = mw.reviewer.card; note = card.note()
    if mw.state != "review" or mw.reviewer.state != 'answer' or not card or card.model()["name"] != "Excerpt Vocabulary": #redefine is only for modifying definitions of Excerpt Vocabulary notes
        return

    selection = mw.web.selectedText().strip().lower() #anki main review area is a QWebEngineView called mw.web #remove leading/trailing space
    if selection in engdict.keys():
        mw.checkpoint(_("Redefine")) #Allow for Undo
        
        worddef = '<br>'.join(engdict.get(note['Word'],'')) + '<br><br>' #preface with worddef if it exists
        newdefn = worddef + selection.capitalize() + '<br>' + '<br>'.join(engdict[selection])         
        changeDefinition(card,note,newdefn)
def highlight():
    card = mw.reviewer.card; note = card.note()
    if mw.state != "review" or mw.reviewer.state != 'answer' or not card or card.model()["name"] != "Excerpt Vocabulary":
        return #highlight is only for modifying definitions of Excerpt Vocabulary notes
    
    selection = mw.web.selectedText().strip()  
    defn = note['Definition']
    marked = re.search('<mark>'+selection+'</mark>',defn)
    if selection and not marked:
        mw.checkpoint(_("Highlight")) #Allow for Undo
        newdefn = defn.replace(selection,'<mark>'+selection+'</mark>') #use HTML <mark> tag to highlight
        changeDefinition(card,note,newdefn)
    else:
        mw.checkpoint(_("Remove Highlight")) #Allow for Undo
        newdefn = defn.replace('<mark>','').replace('</mark>','')
        changeDefinition(card,note,newdefn)
def changeDefinition(card,note,newdefn):
    note['Definition'] = newdefn # update Definition field
    
    note.flush(); card.flush()
    card.load()
    mw.reviewer._showAnswer() # refresh
def onRevert(action_name):
    if action_name == _("Highlight") or _("Redefine"):
        mw.reviewer._showAnswer()
#


