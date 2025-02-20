import serial
import configparser
from time import sleep
import socket
import sqlite3

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
        conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        cur = conn.cursor()
        cur.execute('select * from node')
        data = cur.fetchall()
        conn.close()
        try:
            self.remoteip = data[0][7]
        except:
            self.remoteip = ""
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")
        self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))
        #self.ConnectedMode = cf.get("ScannerConfig", "ConnectedMode")
        # cf = configparser.ConfigParser()
        # cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        # self.sname = cf.get("ScannerConfig", "sname")
        # self.baurate = cf.get("ScannerConfig", "baurate")
        # self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))
        # #self.scannerName = cf.get("ScannerConfig", "scannerName")
        # self.IP = cf.get("ScannerConfig", "IP")
        # self.DDNS = cf.get("ScannerConfig", "DDNS")
        # self.port = int(cf.get("ScannerConfig", "port"))
        # self.ConnectedMode = cf.get("ScannerConfig", "ConnectedMode")
        if self.remoteip != None and len(self.remoteip) >= 6:
            self.condition = True
            count = 0
            try:
                while self.condition == True:
                    try:
                        self.ip = data [count][0]
                        self.port = int(data [count][0])
                        count = count + 1
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((self.IP, self.port))
                        comm=b'\x7e\x04\x01\x24\xda\xff'
                        s.send(comm)
                        data = s.recv(1024)
                    #詳細資料內容
                    #for i in range (int(data[1])):
                    #    print ('Received data: ' ,i," ", hex(data[i]))
                        s.close()
                        print("Socket連接Node" , count,"成功")
                    except:
                        self.condition = False

                    self.show837()
                # self.scannerName="AR837"
                # self.connect="Success"
            except:
                print("Socket連接Node" , count ,"失敗")
            self.scannerName="AR837"
        elif self.remoteip == None or len(self.remoteip) <= 6:              
            try:
                nodestatus=[0,0]
                nodetimetemp = None
                self.nodetime=None
                for x in range(self.nodesCount):
                    node=x+1            
                    xor=255^node^int("0x24",16)
                    sum=node+int("0x24",16)+xor
                    sum =sum % 256
                    comm=b'\x7e\x04'+ bytes([node])+ bytes([int("0x24",16)]) + bytes([xor])+ bytes([sum])
                    #print('send : '+ str(func))
                    ser = serial.Serial(self.sname, self.baurate, timeout=1)
                    ser.write(comm)
                    sleep(0.2)
                    output = ser.read(64)
                    nodestatus[x] = output
                                    
                for x in range(self.nodesCount):
                    try:        
                        if nodestatus[x]!=b'':
                            if nodestatus[x][0]==0x7e:
                                self.scannerName="AR721"
                                self.connect="Success"
                                nodetimetemp=(
                                    "20" + str(nodestatus[x][11]).zfill(2) +
                                        "-" + str(nodestatus[x][10]).zfill(2) +
                                        "-" + str(nodestatus[x][9]).zfill(2) +
                                        " " + str(nodestatus[x][7]).zfill(2) + 
                                        ":" + str(nodestatus[x][6]).zfill(2) +
                                        ":" + str(nodestatus[x][5]).zfill(2)
                                        
                            )
                                if nodetimetemp != None:
                                    self.nodetime = nodetimetemp
                    except:
                        pass                    
                if self.nodetime == None:
                    self.scannerName="R35C"
                self.show()
            except Exception as n:
                print(n)
                self.scannerName="None"
        else:
            self.scannerName="None"

        

    def show837(self):
            self.conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
            self.cur = self.conn.cursor()
            self.cur.execute('select * from node')
            showdata = self.cur.fetchall()
            self.conn.close()
            print("__________node show__________")
            n = 0
            self.condition = True
            while  self.condition == True :
                try:
                    self.nodeid = showdata[n][2]
                    self.nodehostname = showdata[n][4]
                    self.nodeip = showdata[n][7]
                    self.nodeport = showdata[n][8]
                    self.nodebaurate = showdata[n][11]
                    self.nodesname = showdata[n][12]
                    self.nodestatus = showdata[n][14]
                    n = n + 1
                    print("第",n,"台卡機")
                    print("node number=" , self.nodeid )
                    print("nodehostname = " ,self.nodehostname)
                    print("ip= " , self.nodeip)
                    print("prot = " , self.nodeport)
                    print("baurate = " , self.nodebaurate)
                    print("sname = " , self.nodesname)
                    print("status = " , self.nodestatus)
                    print("")  
                except:
                    self.condition = False
                    
    def show(self):
        print("__________ScannerModel show__________")
        print("門口機名稱 = " + self.scannerName)
        print("門口機連線狀態 = " + self.connect)
        print("連線端口 = " + self.sname)
        print("連線速率 = " + self.baurate)
        print("門口機數量 = " , self.nodesCount)
        print("門口機時間 = " , self.nodetime)
        print("")
    
        
