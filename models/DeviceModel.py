import sqlite3
import configparser
import subprocess
class DeviceModel:
    dev_id=''
    name = ''
    family = ''
    mode = ''
    style = ''
    doortype = ''
    is_booking = ''
    localip = ''
    localport = ''
    opendoortime = 2
    authorization_buffer_minutes = 0
    devicetime=''
    
  
    
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.localport = cf.get("DeviceConfig", "defaultport")
        serverip =  cf.get("ServerConfig", "serverip")
        forceLocalIp =  cf.get("DeviceConfig", "forceLocalIp")
        if forceLocalIp == 'true' :
            self.localip = cf.get("DeviceConfig", "defaultip")
        else :
            self.localip = self.getLocalipByServer()

        conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        cur = conn.cursor()
        cur.execute('select * from device')
        data = cur.fetchone()
        conn.close()
        if data != None:
            self.dev_id = data[0]
            self.name = data[5]
            self.family = data[4]
            self.mode = data[8]
            self.style = data[9]
            self.doortype = data[10]
            self.is_booking = data[11]
            self.localip = data[1].split(':',1)[0]
            self.localport = data[1].split(':',1)[1]

        if self.doortype=='一般':
            self.opendoortime =(int)(cf.get("DeviceConfig", "opendoortime_normal"))
        else:
            self.opendoortime =(int)(cf.get("DeviceConfig", "opendoortime_iron"))

        self.authorization_buffer_minutes = (int)(cf.get("DeviceConfig", "authorization_buffer_minutes",  fallback=0))
        self.devicetime = subprocess.getoutput("date")

        self.show()


    def show(self):
        print("__________DeviceModel show__________")
        print("name = " , self.name)
        print("family = " , self.family)
        print("mode = " , self.mode)
        print("doortype = " , self.doortype)
        print("localip = " , self.localip)
        print("localport = " , self.localport)
        print("opendoortime = " , self.opendoortime)
        print("devicetime = " , self.devicetime)

    def getLocalipByServer(self):
        # 先從tun0 , 抓取ip
        cmd = "/sbin/ip -o -4 addr list tun0 | awk '{print $4}' | cut -d/ -f1"
        output = subprocess.getoutput(cmd)
        if "not exist" not in output: 
            return output
        else:
            # 如果抓不到 在找eth0
            cmd = "/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1"
            output = subprocess.getoutput(cmd)
            if "not exist" not in output: 
                return output
        return ""
    
        
