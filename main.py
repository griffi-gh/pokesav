import sys
import time
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog
import design

addrmap = {
    'pname':[0x2598,0xb],
    'money':[0x25F3,0x3],
    'checksum':[0x3523,0x1]
}

charmap={
    '':0x00, #Nothing
    '<page>':0x49, #Begins a new Pokedex page
    '<PKMN>':0x4a, #Prints <PK><MN>
    '<_cont>':0x4b, #Stops and waits for confirmation before scrolling the dialogue down by 1
    '<nl>':0x4e, #New line in dialogue
    '<el>':0x4f, #Write at the last line of dialogue
    '<end>':0x50, #End of string
    '<para>':0x51, #Begin a new dialogue page with button confirmation ("paragraph")
    '<player>':0x52, #Prints player name
    '<rival>':0x53, #Prints rival name
    '<poke>':0x54, #Prints Poké
    '<......>':0x56, #Prints 2 ellipses, "……" (2sym)
    '<done>':0x57, #Ends text box
    '<promt>':0x58, #Prompts to end textbox
    '<target>':0x59, #Prints target pokemon in battle
    '<user>':0x5a, #Prints user pokemon in battle
    '<PC>':0x5b, #Prints PC
    '<TM>':0x5c, #Prints TM
    '<TRAINER>':0x5d, #Prints TRAINER
    '<ROCKET>':0x5e, #Prints ROCKET
    '<dex>':0x5f, #Displays a period and ends the Pokédex entry
    'A':0x80,
    'B':0x81,
    'C':0x82,
    'D':0x83,
    'E':0x84,
    'F':0x85,
    'G':0x86,
    'H':0x87,
    'I':0x88,
    'J':0x89,
    'K':0x8a,
    'L':0x8b,
    'M':0x8c,
    'N':0x8d,
    'O':0x8e,
    'P':0x8f,
    'Q':0x90,
    'R':0x91,
    'S':0x92,
    'T':0x93,
    'U':0x94,
    'V':0x95,
    'W':0x96,
    'X':0x97,
    'Y':0x98,
    'Z':0x99,
    '(':0x9a,
    ')':0x9b,
    ':':0x9c,
    ';':0x9d,
    '[':0x9e,
    ']':0x9f,
    'a':0xa0,
    'b':0xa1,
    'c':0xa2,
    'd':0xa3,
    'e':0xa4,
    'f':0xa5,
    'g':0xa6,
    'h':0xa7,
    'i':0xa8,
    'j':0xa9,
    'k':0xaa,
    'l':0xab,
    'm':0xac,
    'n':0xad,
    'o':0xae,
    'p':0xaf,
    'q':0xb0,
    'r':0xb1,
    's':0xb2,
    't':0xb3,
    'u':0xb4,
    'v':0xb5,
    'w':0xb6,
    'x':0xb7,
    'y':0xb8,
    'z':0xb9,
    'é':0xba,
    "<'d>":0xbb, #Prints 'd as one character
    "<'l>":0xbc, #Prints 'l as one character
    "<'s>":0xbd, #Prints 's as one character
    "<'t>":0xbe, #Prints 't as one character
    "<'v>":0xbf, #Prints 'v as one character
    "'":0xe0,
    '<PK>':0xe1, #Prints PK as one character
    '<MN>':0xe2, #Prints MN as one character
    '-':0xe3,
    "<'r>":0xe4, #Prints 'r as one character
    "<'m>":0xe5, #Prints 'm as one character
    '?':0xe6,
    '!':0xe7,
    '.':0xe8,
    'ァ':0xe9,
    'ゥ':0xea,
    'ェ':0xeb,
    '▷':0xec,
    '▶':0xed,
    '▼':0xee,
    '♂':0xef,
    '₽':0xf0,
    '×':0xf1,
    '.':0xf2,
    '/':0xf3,
    ',':0xf4,
    '♀':0xf5,
    '0':0xf6,
    '1':0xf7,
    '2':0xf8,
    '3':0xf9,
    '4':0xfa,
    '5':0xfb,
    '6':0xfc,
    '7':0xfd,
    '8':0xfe,
    '9':0xff
}

global sav
global ram

def binstr(val):
    return '{0:08b}'.format(val)

def dval(d,v):
    return list(d.keys())[list(d.values()).index(v)]
    
#def setv(sv,ma,value):

def h2c(hexv):
    return str(dval(charmap,hexv))

def topkhex(st):
    hexv=[]
    special=False
    spec=''
    for i in range(len(st)):
        if st[i]=='>':
            special=False
            hexv.append(charmap['<'+spec+'>'])
            continue
        
        if st[i]=='<':
            special=True
            spec=''
            continue
        
        if special:
            spec+=st[i]
        else:
            hexv.append(charmap[st[i]])
    return hexv
            
            
def readram(sv,m):
    value=[]
    for x in range(m[0],m[0]+m[1]):
        value.append(sv[x])
    return value

def readramStr(sv,m):
    raw=readram(sv,m)
    out=''
    for x in range(len(raw)):
        out+=h2c(raw[x])
    return out

def writeRam(sv,v,m,nowr=False):
    vlen=len(v)
    x=0
    for i in range(m[0],m[0]+m[1]):
        if x<vlen:
            val=v[x]
            sv[i]=v[x]
        else:
            if not(nowr):
                sv[i]=0x0
        x+=1

def checksum(sv):
    chs=0xff
    for v in sv[0x2598:0x3523]:
        chs-=v
    return chs&0xff

def fixchecksum(sv):
    fin=checksum(sv)
    sv[0x3523]=fin
    return fin

def save(sav2,ram2):
    sav2.seek(0,0)
    sav2.write(ram2)

def loadfile(file):
    savrd=open(file,'rb+')
    ramrd=bytearray(savrd.read())
    return ramrd,savrd

sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1) 
sys.excepthook = exception_hook

buttons=['Save','Change player name']
            
class qtApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('pokesav')
        self.pushButton.clicked.connect(self.browse)
        self.listWidget.itemDoubleClicked.connect(self.edit)
    def inp(self,a='Set value',b='Enter new value:'):
        return QInputDialog.getText(self,a,b)
    def browse(self):
        self.listWidget.clear()
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/')[0]
        if fname:
            global ram
            global sav
            ram,sav = loadfile(fname)
            self.listWidget.addItem(fname)
            self.listWidget.addItem(buttons[0])
            self.listWidget.addItem(buttons[1])
            self.listWidget.addItem('Current name:'+readramStr(ram,addrmap['pname']))
    def edit(self,item):
        if item.text()==buttons[0]:
            fixchecksum(ram)
            save(sav,ram)
        elif item.text()==buttons[1]:
            t,o=self.inp()
            if o:
                t=t+'<end>'
                writeRam(ram,topkhex(t),addrmap['pname'])
            
                
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = qtApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
