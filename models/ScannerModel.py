import serial
import configparser
from time import sleep
class ScannerModel:
    sname = ''
    baurate = ''
    nodesCount = 1
    block = 1
    nodetime=''
    connect=''
    scannerName=''
    
  
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")
        self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))
        #self.scannerName = cf.get("ScannerConfig", "scannerName")

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
            self.scannerName="None"
        self.show()

    def show(self):
        print("__________ScannerModel show__________")
        print("name = " + self.scannerName)
        print("Connect = " + self.connect)
        print("sname = " + self.sname)
        print("baurate = " + self.baurate)
        print("nodesCount = " , self.nodesCount)
        print("nodesTime = " , self.nodetime)
        
      
        
