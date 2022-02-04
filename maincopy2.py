#!/usr/bin/python3
# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import models.relay as relay
#import models.nfc as nfc
#import models.ar721 as ar721

import models.r35c as r35c
import atexit
import threading
import WebApiClent.remote as remote
import WebApiClent.api as api
import socket
import json
import base64
import WebApiClent.offline as offline

init_flag = True
serverip ="35.229.182.144"
checkip="114.35.246.11"
serverport= 80
token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"
clientip = "220.128.141.137"
localport =4661
#localip = "172.17.22.138"
rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
token_key=b'hhinfo:20200116221039'

def getlocalip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((serverip, 80))
    print(s.getsockname()[0])
    ip = str(s.getsockname()[0])
    s.close()
    return ip


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

#def nfc_callback(no, block):
#    print ("revice nfc call back", no, " : ", block)
#    if no > 0:
#        for x in block:
#            print(x, end='')
#        print(" ")
#        print(str(block, 'UTF-8'))
#        sxstatus = relay.read_sensor()
#        rxstatus = relay.relaystatus
        #clientip1="220.128.141.137"
        #rc = remote.dcode(token, block, clientip1, 1, rxstatus, sxstatus)
        #uid = str(uid).zfill(10)
#        rc = remote.dcode(token, block, clientip, 1, rxstatus, sxstatus)
        
        
#        print ("return",rc)
#        if len(rc) > 10:
#            rc = rc[1:]
            #act = relay.command(str(rc, 'UTF-8'))
#            act = relay.command(rc)
#            remote.operdo(token,clientip,act)
#        print("get data")
#        print(rc)
#    else:
#        print("read nfc error")

#def ar721_callback(datestring, uid):
#    print ("revice nfc call back", datestring, " : ", uid)
#    if uid > 0:
#        sxstatus = relay.read_sensor()
#        rxstatus = relay.relaystatus
#        #clientip="220.128.141.137"
#        uid =str(uid).zfill(10)
#        rc = remote.dcode(token,uid, clientip, 1, rxstatus, sxstatus)
#        print ("return",rc)
#        if len(rc) > 10:
#            rc = rc[1:]
#            #act = relay.command(str(rc, 'UTF-8'))
#            act = relay.command(rc)
#            remote.operdo(token,clientip,0)
#            #rxstatus = relay.relaystatus
#            #sxstatus = relay.read_sensor()
#            #remote.scode(clientip,rxstatus,sxstatus)
# 
#        
#    else:
#        print("read nfc error")
def r35c_callback(uid):
    print ("revice nfc call back uid : ", uid)
    if uid != '' :
        sxstatus = relay.read_sensor()
        rxstatus = relay.relaystatus
        #clientip="220.128.141.137"
        uid =str(uid).zfill(10)
        rc = remote.dcode(token,uid, clientip, 1, rxstatus, sxstatus)
        print ("return",rc)
        if len(rc) > 10:
            rc = rc[1:]
            #act = relay.command(str(rc, 'UTF-8'))
            act = relay.command(rc)
            remote.operdo(token,clientip,0)
            #rxstatus = relay.relaystatus
            #sxstatus = relay.read_sensor()
            #remote.scode(clientip,rxstatus,sxstatus)
        else:
            #offline check 
            offline.checkdoor(uid)
    else:
        print("read nfc error")



def cleanup():
    try:
        relay.cleanup()
    except:
        print("end")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #read config
    with open('/home/ubuntu/nfc/config.json', 'r') as reader:
        jf = json.loads(reader.read())
        serverip  = jf['serverip']
        serverport = jf['serverport']
        clientip = jf['clientip']
        localport =jf['localport']
        block = jf['block']
        checkip= jf['checkip']
        print (serverip,clientip,block,serverport)
    
    init_flag = False
    print_hi('Start')
    clientip = getlocalip()
    atexit.register(cleanup)
    relay.setup()
    relay.start_relay()
    #loop for wait nfc
    #t = threading.Thread(target=nfc.do_read_mifare, args=(block, nfc_callback))
    #t.setDaemon(True)
    #t.start()
    #loop for ar721
    #ar721.init()
    #t =  threading.Thread(target=ar721.do_read_ar721, args=(block,ar721_callback))
    #t.setDaemon(True)
    #t.start()
    t = threading.Thread(target=r35c.do_read_r35c, args=(block,r35c_callback))
    t.setDaemon(True)
    t.start()



    # loop for report every 5 min
    remote.serverip = serverip
    remote.port = serverport
    remote.localport =localport
    t1 = threading.Thread(target=remote.report, args=(clientip, "9999099990",token))
    t1.setDaemon(True)
    t1.start()
    
    #loop for sensor change 
    t2 = threading.Thread(target=remote.monitor_sensor, args=(clientip,token))

    t2.setDaemon(True)
    t2.start()


    #offline.checkdoor("0801535909")
    #api.serverip = serverip
    api.serverip  = checkip
    api.controlip = clientip
    api.port = localport
    api.token_key=token_key
    encoded = base64.b64encode(token_key)
    print ("token=", encoded)
    print (api.controlip)
    api.run()
    #c = " "
    #while c != "Y":
    #    c = input("Do you want to stop ? (Y/N)")
    relay.cleanup()









