import socket
from time import sleep
from datetime import datetime

#import WebApiClient.remote as remote
import configparser
import os
import sqlite3
global node
global host
global port
conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
cur = conn.cursor()
cur.execute('select * from node')
nodedata = cur.fetchall()
conn.close()
#本程式只讀取卡號後傳給chkcard處理
    # cf = configparser.ConfigParser()
    # cf.read("/home/ubuntu/hhinfo_PI/config.ini")
    # host = cf.get("ScannerConfig", "IP")
    # DDNS = cf.get("ScannerConfig", "DDNS")
    # port = int(cf.get("ScannerConfig", "port"))
    # #host = '192.168.16.241'
    # #host = 'iiiservice.synology.me'
    # #port = 1621

def callback(uid,node,host,port):
    print("__________do_read_ar837________________")
    uid =str(uid).zfill(10)
    print(uid)
    chkcard.chkcard(uid,node,host,port)


def write_command_to_node(node, func ,host ,port,hostname):
    xor=255^node^int(func,16)
    sum=node+int(func,16)+xor
    sum =sum % 256
    comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(comm)
        data = s.recv(1024)
        #詳細資料內容
        #for i in range (int(data[1])):
        #    print ('Received data: ' ,i," ", hex(data[i]))
        s.close()  
        return data
    except:
        print("Socket連接Node:",node,"失敗，IP:",host,"名稱",hostname)
        return "error"
           

def write_command_to_node_reboot(node, func ,host ,port,hostname):
    xor=255^node^int(func,16)^int("FD",16)
    sum=node+int(func,16)+int("FD",16)+xor
    sum =sum % 256
    comm=b'\x7e\x05'+ bytes([node])+ bytes([int(func,16)])+ bytes([int("FD",16)]) +bytes([xor])+ bytes([sum])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(comm)
        data = s.recv(1024)
    #詳細資料內容
    #for i in range (int(data[1])):
    #    print ('Received data: ' ,i," ", hex(data[i]))
        s.close()  
        return data
    except:
        print("Socket連接Node:",node,"失敗，IP:",host,"名稱",hostname)
        return "error"
           
def reboot():
    condition = True
    nodecounting = 0
    while condition == True:
        x = nodecounting 
        nodecounting = nodecounting + 1
        try:       
            host = nodedata[x][7]
            port = int(nodedata[x][8])
            hostname = nodedata[x][4]
            node = int(nodedata[x][2])
            if int(nodedata[x][14])==1:
                output=write_command_to_node(node, '0x25',host ,port,hostname)
                #print("讀取資料長度=",output[1],"讀取時間:",str(datetime.now()))
                sleep(1)
                if  len(output) != "error" and (len(output)>=12 ):                    
                    write_command_to_node_reboot(node,'0xA6',host,port,hostname)
                    print("重啟Node:",node,"IP:",host,"名稱",hostname)

            else:
                print("NODE:",node,"IP:",host,"名稱:",hostname,"未啟用")
        except:
            condition = False

reboot()
