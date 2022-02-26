import json
import requests
import datetime
import login_internet as login_internet 
import update_time as update_time
import netifaces as ni
import sqlite3

serverip = "114.35.246.115"
port = 8080

def updatetime():
    path = '/api/v1/data/time'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path
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
    # ni.ifaddresses('tun0')
    # controlip = ni.ifaddresses('tun0')[2][0]['addr']
    # print(controlip)
    controlip='10.8.1.151'  #先手動設定, 正式上線再自動抓取

    controlip = str(controlip)+':4661'   #controlip
    path = '/api/v1/data/device'
    request_string = "ip=" + str(controlip)
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path
    response = requests.get(api_url_base,params=request_string, headers=headers) 
    if response.status_code==200:
        print("伺服器連線成功")
        r = response.json()
        revice_data = r['data']
        conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS device(id TEXT,ip TEXT,local_ip TEXT,ip_mode TEXT,family TEXT,name TEXT,description TEXT,group_id TEXT,mode TEXT,style TEXT,type TEXT,is_booking TEXT,status TEXT,kernel TEXT)')
        c.execute('DELETE FROM device')
        c.execute("INSERT INTO device values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (revice_data["id"],revice_data["ip"],revice_data["local_ip"],revice_data["ip_mode"],revice_data["family"],revice_data["name"],revice_data["description"],revice_data["group_id"],revice_data["mode"],revice_data["style"],revice_data["type"],revice_data["is_booking"],revice_data["status"],revice_data["kernel"],))
        conn.commit()
        conn.close()
    else:
        print("伺服器連線失敗")


updatetime()

#暫時不要登入VPN, 因測試機在外部, 否則會錯誤
# serverip ="35.221.198.141"
# VPNserverip="10.8.0.1"
# netstatus=0
# login_internet.main(serverip, VPNserverip,netstatus)

updatedevice()


# if __name__ == "__main__":
#     serverip = "114.35.246.115"
#     port = 8080
#     updatetime()