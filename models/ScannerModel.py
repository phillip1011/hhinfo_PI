import serial
import configparser
from time import sleep
class ScannerModel:
    name = ''
    sname = ''
    baurate = ''
    block = 1
    
    
  
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.sname = cf.get("ScannerConfig", "sname")
        self.baurate = cf.get("ScannerConfig", "baurate")
        ser = serial.Serial(self.sname, self.baurate, timeout=1)
        input=b'\x7e\x04\x01\x25\xdb\x01'
        ser.write(input)
        sleep(0.2)
        output=ser.read(64)
        
        if output!=b'':
            self.name="AR721"
        else:
            self.name="R35C"
        self.show()
    
    def show(self):
        print("__________ScannerModel show__________")
        print("name = " + self.name)
        print("sname = " + self.sname)
        print("baurate = " + self.baurate)
      
        
