#!/usr/bin/python3
import json
import requests
#import WebApiClient.login_internet as login_internet 
import sqlite3
#import configparser
import globals
import sound as sound
import os
from time import sleep
import socket #get ip
import fcntl  #get ip
import struct #get ip


_deviceid = -1


def cfgupdate():
    globals.initDatabase()
    globals.bootServer()

def initGlobals():
    globals.initializeWithOutGPIO()

def get_ip_address(interface):
    # 創建一個UDP套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
    # 使用ioctl取接口的信息
    ip_address = None
    try:
        ip_address = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface[:15].encode())
        )[20:24])
    except Exception as e:
        ip_address = ""
        print("Error:", e)
    finally:
        s.close()
    
    return ip_address
def mac_get():
    ethact = None #網卡狀態啟用先設為NONE
    try:
        ethact = open('/sys/class/net/eth0/carrier').readline() #取RJ45網卡狀態
    except:
        pass
    if ethact == None: #只有WIFI網卡
        devicemac=open('/sys/class/net/wlan0/address').readline()
    else:  #有RJ45孔網卡
        devicemac=open('/sys/class/net/eth0/address').readline() #取MAC    
    devicemac=devicemac[0:17] #去掉空白值
    return devicemac

def updatedevice():
    global _deviceid
    path = '/api/v1/data/device'
    devicemac=mac_get()
    deviceip = get_ip_address("tun0")
    request_string = "mac=" + devicemac
    request_ipstring = "ip=" + deviceip +":4661"
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + globals._bootServer.serverip + path
    #sample URL= http://35.221.198.141:80/api/v1/data/device
    try :
        response = requests.get(api_url_base,params=request_string, headers=headers, timeout=3)
        if response.status_code==200:            
            r = response.json()
            revice_data = r['data']
            print("Get server/api/v1/data/device 成功")
            if revice_data == None:
                response = requests.get(api_url_base,params=request_ipstring, headers=headers, timeout=3)         
                r = response.json()
                revice_data = r['data']        
            if revice_data == None:
                print('無法從伺服器取得Device資料')
                return 0
            _deviceid = str(revice_data['id'])
            conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
            c=conn.cursor()
            c.execute('DELETE FROM device')
            value = revice_data

            c.execute('INSERT INTO device values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
            value["id"],
            value["ip"],
            value["mac"],
            value["local_ip"],
            value["ip_mode"],
            value["family"],
            value["name"],
            value["description"],
            value["group_id"],
            value["mode"],
            value["style"],
            value["type"],
            value["is_booking"],
            value["status"],
            value["kernel"],
            value["time_buffer_start"],
            value["time_buffer_end"],
            value["spcard_time"],  
            value["node_protocol"],  
            value["powered_by_time"]  
                )
            )
            conn.commit()
            conn.close()
            
        else:
            print("Get server/api/v1/data/device 失敗. 伺服器回傳狀態 : ",response.status_code)
    except:
        print("Get server/api/v1/data/device 錯誤.更新Device失敗")

    if _deviceid == -1:
        conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        cur = conn.cursor()
        cur.execute('select * from device')
        data = cur.fetchall()
        conn.close()
        _deviceid=data[0][0]
        _deviceid=_deviceid[0:1]
def updateNodes(_deviceid):
    path = '/api/v1/data/node' 
    request_string = "device_id=" + str(_deviceid)

    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + globals._bootServer.serverip +path

    try:
        response = requests.get(api_url_base,params=request_string, headers=headers, timeout=3)
        r = response.json()
        revice_data = r['data']
        if response.status_code==200:                                                                           
            print("Get server/api/v1/data/node 成功")
            r = response.json()
            if len(revice_data) < 1:
                print("無NODE DB資料")
                return 0
            nodeValue = revice_data
            # Connect to the SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect('cardno.db')
            cursor = conn.cursor()
            # Create the node table if it doesn't exist
            cursor.execute('DELETE FROM node')
            cursor.execute('''CREATE TABLE IF NOT EXISTS node (
                            id INTEGER PRIMARY KEY,
                            brand TEXT,
                            address TEXT,
                            door_type TEXT,
                            hostname TEXT,
                            outbound_ip TEXT,
                            outbound_port TEXT,
                            inbound_ip TEXT,
                            inbound_port TEXT,
                            mac TEXT,
                            port TEXT,
                            baurate TEXT,
                            sname TEXT,
                            note TEXT,
                            status INTEGER,
                            synced_at TEXT,
                            created_at TEXT,
                            updated_at TEXT
                            )''')
            # Insert data from nodeValue list into the node table
            for node in nodeValue:
                cursor.execute('''INSERT INTO node (
                    id, brand, address, door_type, hostname,
                    outbound_ip, outbound_port, inbound_ip, inbound_port,
                    mac, port, baurate, sname, note, status,
                    synced_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (node['id'], node['brand'], node['address'], node['door_type'],
                node['hostname'], node['outbound_ip'], node['outbound_port'],
                node['inbound_ip'], node['inbound_port'], node['mac'], node['port'],
                node['baurate'], node['sname'], node['note'], node['status'],
                node['synced_at'], node['created_at'], node['updated_at']))
    # Commit changes and close connection
            conn.commit()
            conn.close()

            conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
            cur = conn.cursor()
            cur.execute('select * from node')
            data = cur.fetchall()
            conn.close()
            print("__________node show__________")
            n = 0
            condition = True
            while condition == True:
                try:
                    nodeid = data[n][2]
                    nodehostname = data[n][4]
                    nodeip = data[n][7]
                    nodeport = data[n][8]
                    nodebaurate = data[n][11]
                    nodesname = data[n][12]
                    nodestatus = data[n][14]
                    n = n + 1
                    print("第",n,"台卡機")
                    print("node number=" ,  nodeid )
                    print("nodehostname = " ,nodehostname)
                    print("ip= " , nodeip)
                    print("prot = " , nodeport)
                    print("baurate = " , nodebaurate)
                    print("sname = " , nodesname)
                    print("status = " , nodestatus)
                    print("  ")
                except:
                    condition= False
        else:
            print("Get server/api/v1/data/node 失敗. 伺服器回傳狀態 : ",response.status_code)
    except:
        print("Get server/api/v1/data/node 錯誤")


if __name__=='__main__':
    os.system("sudo systemctl stop hhinfo_main.service")   #先關閉主程式, 等boot.service Finish後再開始
    sound.sysStartSound()
    cfgupdate()
    updatedevice()
    initGlobals()
    updateNodes(_deviceid)
    os.system("sudo systemctl start hhinfo_main.service")
    
