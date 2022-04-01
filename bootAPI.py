import json
import requests
import datetime
import WebApiClient.login_internet as login_internet 
import WebApiClient.update_time as update_time
import netifaces as ni
import sqlite3
from models.ServerModel import ServerModel
import configparser

def initServer():
    global _server
    _server = ServerModel() 

def initDefaultDevice():
    global _defaultip
    global _defaultport
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    _defaultip = cf.get("DeviceConfig", "defaultip")
    _defaultport = cf.get("DeviceConfig", "defaultport")


def updatetime():
    path = '/api/v1/data/time'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + _server.serverip + ":" + str(_server.serverport) + path
    response = requests.get(api_url_base) 
    print(response) 
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
def updatedevice():
    path = '/api/v1/data/device'
    request_string = "ip="+_defaultip +':'+str(_defaultport)
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + _server.serverip + ":" + str(_server.serverport) + path
    print (api_url_base,request_string)
    response = requests.get(api_url_base,params=request_string, headers=headers) 

    if response.status_code==200:
        print("伺服器連線成功")
        r = response.json()
        revice_data = r['data']
        print(revice_data)
        conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS device(id TEXT,ip TEXT,local_ip TEXT,ip_mode TEXT,family TEXT,name TEXT,description TEXT,group_id TEXT,mode TEXT,style TEXT,type TEXT,is_booking TEXT,status TEXT,kernel TEXT)')
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
        print("伺服器連線失敗")


if __name__=='__main__':
   
    initDefaultDevice()
    initServer()
    updatetime()
    updatedevice()
    
    #暫時不要登入VPN, 因測試機在外部, 否則會錯誤
    # serverip ="35.221.198.141"
    # VPNserverip="10.8.0.1"
    # netstatus=0
    # login_internet.main(serverip, VPNserverip,netstatus)

    


# if __name__ == "__main__":
#     serverip = "114.35.246.115"
#     port = 8080
#     updatetime()