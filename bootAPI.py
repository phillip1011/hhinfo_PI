#!/usr/bin/python3
import json
import requests
from datetime import datetime
import WebApiClient.login_internet as login_internet 
import WebApiClient.update_time as update_time
import sqlite3
import configparser
import globals
import subprocess
import threading
import sound as sound
import serial
import os
from time import sleep


def initGlobals():
    globals.initializeWithOutGPIO()
 
def update721time():
    nodesCount = globals._scanner.nodesCount
    for x in range(nodesCount):
        node = x+1
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        sysyy=int(datetime.now().strftime('%y'))
        sysmm=int(datetime.now().strftime('%m'))
        sysdd=int(datetime.now().strftime('%d'))
        syshh=int(datetime.now().strftime('%H'))
        sysmin=int(datetime.now().strftime('%M'))
        sysss=int(datetime.now().strftime('%S'))
        sysww=int(datetime.now().strftime('%w'))
        if sysww==0:
            sysww=7
        print("PI系統時間=",sysyy,'-',sysmm,'-',sysdd,' ',syshh,':',sysmin,':',sysss)
        xor=255^node^35^sysss^sysmin^syshh^sysww^sysdd^sysmm^sysyy
        
        sum=(node+35+sysss+sysmin+syshh+sysww+sysdd+sysmm+sysyy+xor)
        sum =sum % 256
        input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
        # print(input)
        ser.write(input)
        sleep(0.2)
        print(globals._scanner.name,"node=",node, "校時完成")
    sound.scannerUpdateTimeFinish()
def updatetime():
    path = '/api/v1/data/time'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) + path
    try :   
        response = requests.get(api_url_base, timeout=3)
        if response.status_code==200:
            print("Get server/api/v1/data/time 成功.")
            r = response.json()
            Srvtime = r['data']
            time_tuple = (
                int(Srvtime[0:4]),
                int(Srvtime[5:7]),
                int(Srvtime[8:10]),
                int(Srvtime[11:13]),
                int(Srvtime[14:16]),
                int(Srvtime[17:19]),
                0, # Millisecond
            )
            _linux_set_time(time_tuple)

            if globals._scanner.name=="AR721":
                update721time()
            return response.status_code        

        else : 
            print("Get server/api/v1/data/time 失敗. 伺服器回傳狀態 : ",response.status_code)
            return response.status_code  
    except:
        print("Get server/api/v1/data/time 錯誤.更新時間失敗")
        return

def updatedevice():
    path = '/api/v1/data/device'
    request_string = "ip="+globals._device.localip +':'+str(globals._device.localport)
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) + path
    
    try :
        response = requests.get(api_url_base,params=request_string, headers=headers, timeout=3) 
        if response.status_code==200:
            print("Get server/api/v1/data/device 成功")
            r = response.json()
            revice_data = r['data']
            if revice_data == None:
                print('無法從伺服器取得Device資料,localip不符')
                return 0
            conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
            c=conn.cursor()
            c.execute('DELETE FROM device')
            c.execute("INSERT INTO device values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                revice_data["id"],
                revice_data["ip"],
                revice_data["local_ip"],
                revice_data["ip_mode"],
                revice_data["family"],
                revice_data["name"],
                revice_data["description"],
                revice_data["group_id"],
                revice_data["mode"],
                revice_data["style"],
                revice_data["type"],
                revice_data["is_booking"],
                revice_data["status"],
                revice_data["kernel"]
                )
            )
            conn.commit()
            conn.close()
        else:
            print("Get server/api/v1/data/device 失敗. 伺服器回傳狀態 : ",response.status_code)
    except:
        print("Get server/api/v1/data/device 錯誤.更新Device失敗")

def read_721time(func):
    #print("ar721-",node," send =",func)
    node=1
    xor=255^node^int(func,16)
    sum=node+int(func,16)+xor
    sum =sum % 256
    comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
    print('send : '+ str(func))
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
    ser.write(comm)
    sleep(0.2)
    output = ser.read(64)

    if len(output)==0:
        print("無回傳資料")
    else:
        print('回傳資料長度=',len(output))
        rtn=''
        for i in range(len(output)):
            rtn=rtn+' '+str(hex(output[i]))

        print(rtn)

        if output[3]==0x3:
            ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
            ScanTime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)

            print('ar721日期=',ScanDate)
            print('ar721時間=',ScanTime)
            
            time_tuple = ( int("20" + str(output[11]).zfill(2)), # Year
                            output[10], # Month
                            output[9], # Day
                            output[7], # Hour
                            output[6], # Minute
                            output[5], # Second
                            0, # Millisecond
                        )
            return time_tuple

def _linux_set_time(time_tuple):
    import ctypes
    import ctypes.util
    import time
    import datetime
    
    #print(time_tuple)
    CLOCK_REALTIME = 0

    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))
    print("ubuntu time update OK")

    ts = timespec()
    ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond
    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

def updateLinuxTime():
    while True:
        if updatetime()==200:
            updatedevice()
            sound.sysTimeUpdateFinish()
            break
        else:
            if globals._scanner.name=="AR721":
                print("Get 721 RTC Start")
                time_tuple=read_721time('0x24')
                _linux_set_time(time_tuple)
                print("Get 721 RTC and update to Linux Finish")
                sound.sysTimeUpdateFinish()
                break
            else:
                sound.sysTimeUpdateFail()
                sleep(300)
                os.system("sudo systemctl restart hhinfo_main.service")
                continue

if __name__=='__main__':
    os.system("sudo systemctl stop hhinfo_main.service")   #先關閉主程式, 等boot.service Finish後再開始
    cf = configparser.ConfigParser()
    cf.read("/home/ubuntu/hhinfo_PI/config.ini")
    
    serverip = cf.get("ServerConfig", "serverip")
    VPNserverip = cf.get("ServerConfig", "VPNserverip")
    forceVPN = cf.get("ServerConfig", "forceVPN")
    os.system("amixer -c 0 set Headphone 100%")  #調整系統音量到100%
    sound.sysStartSound()

    
    initGlobals()
    updateLinuxTime()
    if forceVPN == 'true':
        print('強制啟用VPN')
        login_internet.main(False)
#        if os.system("ip addr |grep tun0")==0:
#            sound.sysLoginVpnSound()

    os.system("sudo systemctl restart hhinfo_main.service")