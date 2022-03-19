import RPi.GPIO as GPIO
import threading
import serial
import sqlite3
from datetime import datetime
from time import sleep
import WebApiClent.login_internet as login_internet
import models.relay as relay
import WebApiClent.api as api
import WebApiClent.remote as remote
import models.r35c as r35c
import models.ar721 as ar721
import chkcard as chkcard
GPIO.setwarnings(False)
global uid

sname='/dev/ttyUSB0'
baurate=9600
token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"
token_key=b'hhinfo:20200116221039'
serverip ="35.221.198.141"
serverport= 80
VPNserverip="10.8.0.1"
checkip="114.35.246.11"
# controlip = "10.8.1.151"
# localport = 4661 
rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]

conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
dev_c=conn.cursor()
dev_c.execute('select * from device')
for row1 in dev_c:
    doortype=row1[10]
    controlip=row1[1].split(':',1)
    localport=controlip[1]
    controlip=controlip[0]
# print('localport=',localport)
# print('controlip=',controlip)
conn.commit()
conn.close()

#123
def ar721_callback(uid,node):
    print('doortype=',doortype)
    uid =str(uid).zfill(10)
    chkcard.chkcard(uid,"AR721",sname,baurate,doortype,node)
    sxstatus = relay.read_sensor()
    rxstatus = relay.relaystatus
    remote.scode(controlip,rxstatus,sxstatus)


def r35c_callback(uid):
    #print ("revice nfc call back uid : ", uid)
    if uid != '' :
        uid =str(uid).zfill(10)
        chkcard.chkcard(uid,"R35C",sname,baurate,doortype)
        sxstatus = relay.read_sensor()
        rxstatus = relay.relaystatus        
        remote.scode(controlip,rxstatus,sxstatus)
    else:
        print("read nfc error")


if __name__=='__main__':
    #loop for change relay off
    relay.setup()
    relay.start_relay()
  

    
    #loop for checking internet every 1 min
    # netstatus=1   # 0表示boot時, 1表示每X分鐘檢查
    # t2 = threading.Thread(target=login_internet.main, args=(serverip, VPNserverip,netstatus))
    # t2.start()

    #loop for card number every 1 sec
    ser = serial.Serial(sname, baurate, timeout=1)
    #input=b'\x7e\x04\x01\x25\xdb\x01'
    isAr721=False
    
   

    #check  721 or r35c
   
 

    input=b'\x7e\x04\x01\x25\xdb\x01'
    ser.write(input)
    sleep(0.2)
    output=ser.read(64)
    
    if output!=b'':
        print("AR721 Start")
        controlname="AR721"
        print(controlname," Start")
        t = threading.Thread(target=ar721.do_read_ar721, args=(sname,baurate))
        t.setDaemon(True)
        t.start()
    else:
        print("R35C Start")
        controlname="R35C"
        print(controlname," Start")
        block=1
        t = threading.Thread(target=r35c.do_read_r35c, args=(block,r35c_callback))
        t.setDaemon(True)
        t.start()

    #loop for report every 3 min
    remote.serverip = serverip
    remote.port = serverport
    remote.localport =localport
    remote.scannername=controlname
    

    t3 = threading.Thread(target=remote.report, args=(controlip, "9999099990",token))
    t3.setDaemon(True)
    t3.start()

    #loop for sensor change every 0.1 sec
    t4 = threading.Thread(target=remote.monitor_sensor, args=(controlip,token))
    t4.setDaemon(True)
    t4.start()

    #start API flask
    api.serverip  = checkip
    api.controlip = controlip
    api.port = 4661
    api.token_key=token_key
    api.sname=sname
    api.baurate=baurate
    api.controlname=controlname
    api.doortype=doortype
    api.run()
