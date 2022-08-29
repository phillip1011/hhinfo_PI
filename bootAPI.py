#!/usr/bin/python3
import json
import requests
import datetime
import WebApiClient.login_internet as login_internet 
import WebApiClient.update_time as update_time
import sqlite3
import configparser
import globals
import subprocess
import threading

def initGlobals():
    globals.initializeWithOutGPIO()
 


def updatetime():
    path = '/api/v1/data/time'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) + path
    try :   
        response = requests.get(api_url_base, timeout=3)
        if response.status_code==200:
            print("Get server/api/v1/data/time 成功.")
            r = response.json()
            time = r['data']
            timeformat =  datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
            update_time.time_tuple = (
                int(timeformat.strftime('%Y')),
                int(timeformat.strftime('%m')),
                int(timeformat.strftime('%d')),
                int(timeformat.strftime('%H')),
                int(timeformat.strftime('%M')),
                int(timeformat.strftime('%S')),
                0, # Millisecond
            )
                #print (update_time.time_tuple)
            update_time.update()
            if globals._scanner.name=="AR721":
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

        else : 
            print("Get server/api/v1/data/time 失敗. 伺服器回傳狀態 : ",response.status_code)
    except:
        print("Get server/api/v1/data/time 錯誤.更新時間失敗")


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


if __name__=='__main__':
   
    cf = configparser.ConfigParser()
    cf.read("/home/ubuntu/hhinfo_PI/config.ini")
    
    serverip = cf.get("ServerConfig", "serverip")
    VPNserverip = cf.get("ServerConfig", "VPNserverip")
    forceVPN = cf.get("ServerConfig", "forceVPN")

    
    initGlobals()
    if forceVPN == 'true':
        print('強制啟用VPN')
        login_internet.main(False)

    
    updatetime()
    updatedevice()