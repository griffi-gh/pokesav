import sys
import time
import os

sav=open(sys.argv[1],'rb+')
ram=bytearray(sav.read())

smap = {
    'pname':{0x2598,0xB,0x50},
    'money':{0x25F3,0x3},
}

def setv(sv,vmap,v):
    

def fixchecksum(sv):
    chs=0xff
    for v in sv[0x2598:0x3523]:
        chs-=v
    fin=chs&0xff
    sv[0x3523]=fin    

def save():
    sav.seek(0,0)
    sav.write(ram)

fixchecksum(ram)
save()
        
    
    
