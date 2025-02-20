import socket
from time import sleep
from datetime import datetime
import chkcard as chkcard
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
           
def cleardata():
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
                write_command_to_node(node,'0x2d',host,port,hostname) #先清空721內的舊記錄
                print("清空資料Node:",node,"IP:",host,"名稱",hostname)
            else:
                print("NODE:",node,"IP:",host,"名稱:",hostname,"未啟用")
        except:
            condition = False
def do_read_ar837():
        #nodesCount = globals._scanner.nodesCount
        #nodesCount=1
        #for y in range(nodesCount):
        #    node = y+1
    cleardata()
    while True:
        condition = True
        nodecounting = 0
        while condition == True:        
            try:                
                if int(nodedata[nodecounting][14])==1:
                    host = nodedata[nodecounting][7]
                    port = int(nodedata[nodecounting][8])
                    hostname = nodedata[nodecounting][4]
                    node = int(nodedata[nodecounting][2])
                    try:
                        sleep(0.4)
                        output=write_command_to_node(node, '0x25',host ,port,hostname)
                        #print("讀取資料長度=",output[1],"讀取時間:",str(datetime.now()))
                        sleep(0.5)
                        if  len(output) != "error" and (len(output)==31 or len(output)==35):
                            today=str(datetime.now().strftime('%Y-%m-%d'))
                            ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
                            ScanTime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)
                            print(ScanDate)
                            print(ScanTime)
                            if today==ScanDate:
                                #if output[3]==0x3 and output[1]==0x1d:   #資料長度應為29或33
                                if output[3]==0x3:
                                    UID =  bytearray(b'\x00\x00\x00\x00')
                                    UID[0] = output[19]
                                    UID[1] = output[20]
                                    UID[2] = output[23]
                                    UID[3] = output[24]
                                    uid = int.from_bytes(UID, byteorder='big')
                                    print('AR837刷卡記錄,站號(node)=',node,'卡號:',uid,'刷卡日期',ScanDate,'刷卡時間',ScanTime)
                                    write_command_to_node(node, '0x37',host,port,hostname)
                                    sleep(0.2)
                                    callback(uid,node,host,port)
                                else :
                                    write_command_to_node(node, '0x37' ,host,port,hostname)
                                    sleep(0.2)
                            # elif len(output)== "error" :
                            #     print("Socket連接Node:",node,"失敗，IP:",host,"名稱",hostname)
                            else:
                                print("讀卡機或主機時間不符,",'讀卡機刷卡日期:',ScanDate,ScanTime,'系統時間:',today)
                                write_command_to_node(node, '0x37',host,port,hostname)
                    except KeyboardInterrupt:
                        print("使用者強制中斷讀取門口機程序")
                        raise
                    except Exception as e:
                        print(e)
                nodecounting = nodecounting + 1
            except:
                condition = False

if __name__=='__main__':
    do_read_ar837()