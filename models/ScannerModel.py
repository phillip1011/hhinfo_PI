import serial
import configparser
from time import sleep
class ScannerModel:
    name = ''
    sname = ''
    baurate = ''
    block = 1
    
    
  
    def __init__(self):
        print("_________ScannerModel run________init_________")
        cf = configparser.ConfigParser()
        cf.read("config.ini")
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
           
    
    def show(self):
        print("ScannerModel show")
        print("name = " + self.name)
      
        
