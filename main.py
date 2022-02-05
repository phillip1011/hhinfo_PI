import RPi.GPIO as GPIO
import threading
import serial
import sqlite3
from datetime import datetime
from time import sleep
import login_internet as login_internet
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
    controlip=row1[1].split(':',1)
    localport=controlip[1]
    controlip=controlip[0]
# print('localport=',localport)
# print('controlip=',controlip)
conn.commit()
conn.close()




def ar721_callback(uid):
    chkcard.chkcard(uid,"AR721")
    sxstatus = relay.read_sensor()
    rxstatus = relay.relaystatus
    remote.scode(controlip,rxstatus,sxstatus)


def r35c_callback(uid):
    #print ("revice nfc call back uid : ", uid)
    if uid != '' :
        uid =str(uid).zfill(10)
        chkcard.chkcard(uid,"R35C")
        sxstatus = relay.read_sensor()
        rxstatus = relay.relaystatus        
        remote.scode(controlip,rxstatus,sxstatus)
        # rc = remote.dcode(token,uid, controlip, 1, rxstatus, sxstatus)
        # print ("return",rc)

        # if len(rc) > 10:
        #     print("線上開門")
        #     rc = rc[1:]
        #     act = relay.command(rc)  #切字完,做RY動作action()
        #     remote.operdo(token,controlip,0)
        # else:
        #     print("離線開門")
        #     chkcard.chkcard(uid)
    else:
        print("read nfc error")


if __name__=='__main__':
    #loop for change relay off
    relay.setup()
    relay.start_relay()
    
    #loop for checking internet every 1 min
    t2 = threading.Thread(target=login_internet.main, args=(serverip, VPNserverip))
    t2.start()

    #loop for card number every 1 sec
    ser = serial.Serial(sname, baurate, timeout=1)
    input=b'\x7e\x04\x01\x25\xdb\x01'
    ser.write(input)
    sleep(0.2)
    output=ser.read(64)
    
    if output!=b'':
        print("AR721 Start")
        t = threading.Thread(target=ar721.do_read_ar721, args=(sname,baurate))
        t.setDaemon(True)
        t.start()
    else:
        print("R35C Start")
        t = threading.Thread(target=r35c.do_read_r35c, args=(block,r35c_callback))
        t.setDaemon(True)
        t.start()  

    #loop for report every 3 min
    remote.serverip = serverip
    remote.port = serverport
    remote.localport =localport
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
    api.run()
#20220101 完成刷卡程式(do_read_r35c)及sensor4開門程式(sx_chk)並加入threading
#20220102 完成網路及VPN連線測試程式(login_internet.py)
#20220103 checkflask 和取得本機IP及OVPN IP完成
#20220104 遠端校時及遠端控制完成 , 刷卡資料已傳送到伺服器並接收動作
#20220105 完成傳送卡號到SRV視同舊系統
#20220108 完成上傳及下傳程式閱讀, 測試SQLite新增
#問題: config.json何時產生出來, 送給WEBAPI?
#問題: 有TR沒清掉, 起第二隻MAIN會無法遠端控制
