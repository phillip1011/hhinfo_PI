import serial
import configparser
from time import sleep
import socket

class ScannerModel:
    sname = ''
    baurate = ''
    nodesCount = 1
    block = 1
    nodetime=''
    connect=''
    scannerName=''
    IP=''   #192.168.16.241
    DDNS='' #iiiservice.synology.me
    port='' #1621
    ConnectedMode=''
  
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")
        self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))
        #self.scannerName = cf.get("ScannerConfig", "scannerName")
        self.IP = cf.get("ScannerConfig", "IP")
        self.DDNS = cf.get("ScannerConfig", "DDNS")
        self.port = int(cf.get("ScannerConfig", "port"))
        self.ConnectedMode = cf.get("ScannerConfig", "ConnectedMode")
        print(self.ConnectedMode)
        if self.ConnectedMode=='Socket':
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.IP, self.port))
                comm=b'\x7e\x04\x01\x24\xda\xff'
                s.send(comm)
                data = s.recv(1024)
                #詳細資料內容
                #for i in range (int(data[1])):
                #    print ('Received data: ' ,i," ", hex(data[i]))
                s.close()
                self.scannerName="AR837"
                self.connect="Success"
            except:
                print("Socket連接Node失敗")
        elif self.ConnectedMode=='uart':              
            try:
                ser = serial.Serial(self.sname, self.baurate, timeout=1)
                input=b'\x7e\x04\x01\x24\xda\xff'    #Soyal 7系統讀取時間指令
                ser.write(input)
                sleep(0.2)
                output=ser.read(64)
                if output!=b'':
                    if output[0]==0x7e:
                        self.scannerName="AR721"
                        self.connect="Success"
                        self.nodetime=(
                            "20" + str(output[11]).zfill(2) +
                                "-" + str(output[10]).zfill(2) +
                                "-" + str(output[9]).zfill(2) +
                                " " + str(output[7]).zfill(2) + 
                                ":" + str(output[6]).zfill(2) +
                                ":" + str(output[5]).zfill(2)
                        )
                else:
                    self.scannerName="R35C"
            except Exception as n:
                print(n)
                #self.scannerName="None"
        else:
            self.scannerName="None"

        self.show()

    def show(self):
        print("__________ScannerModel show__________")
        print("門口機名稱 = " + self.scannerName)
        print("門口機連線狀態 = " + self.connect)
        print("連線端口 = " + self.sname)
        print("連線速率 = " + self.baurate)
        print("門口機數量 = " , self.nodesCount)
        print("門口機時間 = " , self.nodetime)
        print("")
        
      
        
