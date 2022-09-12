import serial
import configparser
from time import sleep
class ScannerModel:
    name = ''
    sname = ''
    baurate = ''
    nodesCount = 1
    block = 1
    nodetime=''
    
    
  
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")
        self.nodesCount = (int)(cf.get("ScannerConfig", "nodesCount",  fallback=1))

        try:
            ser = serial.Serial(self.sname, self.baurate, timeout=1)
            input=b'\x7e\x04\x01\x24\xda\xff'    #Soyal 7系統讀取時間指令
            ser.write(input)
            sleep(0.2)
            output=ser.read(64)
            
            if output!=b'':
                if output[0]==0x7e:
                    self.name="AR721"
                    self.nodetime=(
                        "20" + str(output[11]).zfill(2) +
                         "-" + str(output[10]).zfill(2) +
                         "-" + str(output[9]).zfill(2) +
                         " " + str(output[7]).zfill(2) + 
                         ":" + str(output[6]).zfill(2) +
                         ":" + str(output[5]).zfill(2)
                    )
                else:
                    self.name="R35C"
            else:
                self.name="R35C"
        except Exception as n:
            print(n)
            self.name="None"
        self.show()
    def show(self):
        print("__________ScannerModel show__________")
        print("name = " + self.name)
        print("sname = " + self.sname)
        print("baurate = " + self.baurate)
        print("nodesCount = " , self.nodesCount)
        print("nodesTime = " , self.nodetime)
      
        
