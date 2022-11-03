import json
import subprocess
import serial
import requests
import sound as sound
from datetime import datetime
from time import sleep
import configparser
import globals

class RTCModel:
    RTCDev=''
    Ar721update= ''
    timeUpdate=''
    scannerName=''

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.serverip = cf.get("ServerConfig", "serverip")
        self.serverport = cf.get("ServerConfig", "serverport")
        self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")

        if self.updateLocalTime()==200:
            if globals._scanner.scannerName=="AR721":
                self.update721time()
            if self.updateRTC()==1:
                self.RTCDev="連接成功"
            else:
                self.RTCDev="連接失敗"
            self.timeUpdate='Sucess'
            sound.sysTimeUpdateFinish()
        else:
            if self.findRTC()==1: #有RTC,將RTC寫到721
                if globals._scanner.scannerName=="AR721":
                    self.update721time()
                    sound.sysTimeUpdateFinish()
                    self.timeUpdate='Sucess'
            else: #無RTC,用721回寫到系統
                if globals._scanner.scannerName=="AR721":
                    time_tuple=self.read_721time('0x24')
                    self.localSetTime(time_tuple)
                    self.timeUpdate='Sucess'
                    sound.sysTimeUpdateFinish()
                else: #無網路,無RTC,無721, 
                    sound.sysTimeUpdateFail()
                    self.timeUpdate='fail'
        self.show()


    def show(self):
        print("__________RTCModel show__________")
        print("RTC Device = " , self.RTCDev)
        print("AR721時間更新 = " , self.Ar721update)
        print("檢查時間更新 = " , self.timeUpdate)

    def updateLocalTime(self):
        path = '/api/v1/data/time'
        headers = {'Content-Type': 'application/json'}
        api_url_base = "http://" + self.serverip + ":" + str(self.serverport) + path
        try :   
            response = requests.get(api_url_base, timeout=3)
            if response.status_code==200:
                #print("Get server/api/v1/data/time 成功.")
                r = response.json()
                Srvtime = r['data']
                time_tuple = (
                    int(Srvtime[0:4]),
                    int(Srvtime[5:7]),
                    int(Srvtime[8:10]),
                    int(Srvtime[11:13]),
                    int(Srvtime[14:16]),
                    int(Srvtime[17:19]),
                    0, # Millisecond
                )
                self.localSetTime(time_tuple)
                return response.status_code

            else : 
                print("Get server/api/v1/data/time 失敗. 伺服器回傳狀態 : ",response.status_code)
                return response.status_code  
        except:
            print("Get server/api/v1/data/time 錯誤.更新時間失敗")
        #     return

    def update721time(self):
            nodesCount = self.nodesCount
            for x in range(nodesCount):
                node = x+1
                ser = serial.Serial(self.sname, self.baurate, timeout=1)
                sysyy=int(datetime.now().strftime('%y'))
                sysmm=int(datetime.now().strftime('%m'))
                sysdd=int(datetime.now().strftime('%d'))
                syshh=int(datetime.now().strftime('%H'))
                sysmin=int(datetime.now().strftime('%M'))
                sysss=int(datetime.now().strftime('%S'))
                sysww=int(datetime.now().strftime('%w'))
                if sysww==0:
                    sysww=7
                #print("PI系統時間=",sysyy,'-',sysmm,'-',sysdd,' ',syshh,':',sysmin,':',sysss)
                xor=255^node^35^sysss^sysmin^syshh^sysww^sysdd^sysmm^sysyy
                
                sum=(node+35+sysss+sysmin+syshh+sysww+sysdd+sysmm+sysyy+xor)
                sum =sum % 256
                input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
                # print(input)
                ser.write(input)
                sleep(0.2)
                print(globals._scanner.scannerName,"node=",node, "校時完成")
            self.Ar721update="Success"
            #sound.scannerUpdateTimeFinish()

    def read_721time(self, func):
        #print("ar721-",node," send =",func)
        node=1
        xor=255^node^int(func,16)
        sum=node+int(func,16)+xor
        sum =sum % 256
        comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
        #print('send : '+ str(func))
        ser = serial.Serial(self.sname, self.baurate, timeout=1)
        ser.write(comm)
        sleep(0.2)
        output = ser.read(64)

        if len(output)==0:
            print("無回傳資料")
        else:
            print('回傳資料長度=',len(output))
            rtn=''
            for i in range(len(output)):
                rtn=rtn+' '+str(hex(output[i]))

            #print(rtn)

            if output[3]==0x3:
                ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
                ScanTime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)

                #print('ar721日期=',ScanDate)
                #print('ar721時間=',ScanTime)

                time_tuple = ( int("20" + str(output[11]).zfill(2)), # Year
                                output[10], # Month
                                output[9], # Day
                                output[7], # Hour
                                output[6], # Minute
                                output[5], # Second
                                0, # Millisecond
                            )
                return time_tuple

    def localSetTime(self, time_tuple):
        import ctypes
        import ctypes.util
        import time
        import datetime
        
        #print(time_tuple)
        CLOCK_REALTIME = 0

        class timespec(ctypes.Structure):
            _fields_ = [("tv_sec", ctypes.c_long),
                        ("tv_nsec", ctypes.c_long)]

        librt = ctypes.CDLL(ctypes.util.find_library("rt"))
        

        ts = timespec()
        ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
        ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond
        # http://linux.die.net/man/3/clock_settime
        librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

        #self.bootSysTimeProc='Success'

    def updateRTC(self):
        try:
            subprocess.check_output("sudo hwclock -w",shell=True,timeout=2) #將時間寫入RTC
            return 1
        except:
            return 0

    def findRTC(self):
        try:
            subprocess.check_output("sudo hwclock -r",shell=True,timeout=2) #將讀取RTC時間
            return 1
        except:
            return 0          

