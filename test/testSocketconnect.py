import socket
from time import sleep
from datetime import datetime
#import chkcard as chkcard
#import WebApiClient.remote as remote
#import globals
import os

#本程式只讀取卡號後傳給chkcard處理

host = '192.168.16.241'
#host = 'iiiservice.synology.me'
port = 1621

def callback(uid):
    print("__________do_read_ar721________________")
    uid =str(uid).zfill(10)
    print(uid)
    #chkcard.chkcard(uid)


def write_command_to_node(node, func):
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
        print("Socket連接Node失敗")
    
def do_read_ar721():
    #nodesCount = globals._scanner.nodesCount
    nodesCount=1
    #for y in range(nodesCount):
    #    node = y+1
    #    write_command_to_node(node, '0x2d') #先清空721內的舊記錄

    while True:
       for x in range(nodesCount):
            node = x+1
            output=write_command_to_node(node, '0x25')
            print("讀取資料長度=",output[1],"讀取時間:",str(datetime.now()))
            sleep(1)

            if len(output)==31 or len(output)==35:
                today=str(datetime.now().strftime('%Y-%m-%d'))
                ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
                ScanTime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)
                if today==ScanDate:
                    #if output[3]==0x3 and output[1]==0x1d:   #資料長度應為29或33
                    if output[3]==0x3:
                        UID =  bytearray(b'\x00\x00\x00\x00')
                        UID[0] = output[19]
                        UID[1] = output[20]
                        UID[2] = output[23]
                        UID[3] = output[24]
                        uid = int.from_bytes(UID, byteorder='big')
                        print('AR721刷卡記錄,站號(node)=',node,'卡號:',uid,'刷卡日期',ScanDate,'刷卡時間',ScanTime)
                        write_command_to_node(node, '0x37')
                        sleep(0.2)
                        callback(uid)
                    else :
                        write_command_to_node(node, '0x37')
                        sleep(0.2)
                else:
                    print("讀卡機或主機時間不符,",'讀卡機刷卡日期:',ScanDate,ScanTime,'系統時間:',today)
                    write_command_to_node(node, '0x37')

if __name__=='__main__':
    do_read_ar721()