import sqlite3
import configparser
class DeviceModel:
    name = ''
    family = ''
    mode = ''
    doortype = ''
    localip = ''
    localport = ''
    
  
    def __init__(self):
        print("_________DeviceModel run________init_________")
        conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        cur = conn.cursor()
        cur.execute('select * from device')
        data = cur.fetchone()
        self.name = data[5]
        self.family = data[6]
        self.mode = data[8]
        self.doortype = data[10]
        self.localip = data[1].split(':',1)[0]
        self.localport = data[1].split(':',1)[1]
        conn.commit()
        conn.close()

        # cf = configparser.ConfigParser()
        # cf.read("config.ini")
        # self.port = cf.get("DeviceConfig", "port")
    
    def show(self):
        print("DeviceModel show")
        print("name = " + self.name)
        print("family = " + self.family)
        print("mode = " + self.mode)
        print("doortype = " + self.doortype)
        print("localip = " + self.localip)
        print("localport = " + self.localport)
        
