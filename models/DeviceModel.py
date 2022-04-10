import sqlite3
import configparser
import subprocess
class DeviceModel:
    name = ''
    family = ''
    mode = ''
    doortype = ''
    localip = ''
    localport = ''
    opendoortime = 2
    
    
  
    
    def __init__(self):
        conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        cur = conn.cursor()
        cur.execute('select * from device')
        data = cur.fetchone()
        conn.close()


        cf = configparser.ConfigParser()
        cf.read("config.ini")
        self.localport = cf.get("DeviceConfig", "defaultport")
        serverip =  cf.get("ServerConfig", "serverip")

        if data == None:
            forceLocalIp =  cf.get("DeviceConfig", "forceLocalIp")
            if forceLocalIp == 'true' :
                self.localip = cf.get("DeviceConfig", "defaultip")
            else :
                self.localip = self.getLocalipByServer(serverip)
        else :
            self.name = data[5]
            self.family = data[6]
            self.mode = data[8]
            self.doortype = data[10]
            self.localip = data[1].split(':',1)[0]
            self.localport = data[1].split(':',1)[1]

        if self.doortype=='一般':
            self.opendoortime =(int)(cf.get("DeviceConfig", "opendoortime_normal"))
        else:
            self.opendoortime =(int)(cf.get("DeviceConfig", "opendoortime_iron"))
       
        self.show()


    def show(self):
        print("__________DeviceModel show__________")
        print("name = " + self.name)
        print("family = " + self.family)
        print("mode = " + self.mode)
        print("doortype = " + self.doortype)
        print("localip = " + self.localip)
        print("localport = " + self.localport)
        print("opendoortime = " , self.opendoortime)

    def getLocalipByServer(self,serverip):

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
    
        
