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

global uid

sname='/dev/ttyUSB0'
baurate=9600
token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"
token_key=b'hhinfo:20200116221039'
serverip ="35.221.198.141"
serverport= 80
VPNserverip="10.8.0.1"
checkip="114.35.246.11"
controlip = "10.8.1.151"
localport = 4661 
rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
GPIO.setwarnings(False)

def ar721_callback(uid):
    chkcard.chkcard(uid)

def r35c_callback(uid):
    #print ("revice nfc call back uid : ", uid)
    if uid != '' :
        sxstatus = relay.read_sensor()
        rxstatus = relay.relaystatus
        uid =str(uid).zfill(10)
        rc = remote.dcode(token,uid, controlip, 1, rxstatus, sxstatus)
        print ("return",rc)
        conn=sqlite3.connect("cardno.db")
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scanlog(cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT)')
        today=str(datetime.now().strftime('%Y%m%d'))
        time=str(datetime.now().strftime('%H%M%S')).zfill(6)
        c.execute("INSERT INTO scanlog VALUES(?,?,?,0)", (uid,today,time,))
        conn.commit()
        conn.close()

        if len(rc) > 10:
            print("線上開門")
            rc = rc[1:]
            act = relay.command(rc)  #切字完,做RY動作action()
            remote.operdo(token,controlip,0)
        else:
            print("離線開門")
            #offline.checkdoor(uid)  #VIPCards
            chkcard.chkcard(uid)            #一般卡
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
        block=1
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
