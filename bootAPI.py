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