import configparser


class ServerMode2:
    token = ''
    #token_key = ''
    serverip = ''
    serverport = ''
    VPNserverip = ''
    verifyserverip = '' 
    #forceVPN=''
    poweredByTime=''
  
    
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.token = cf.get("ServerConfig", "token")
        #self.token_key = cf.get("ServerConfig", "token_key")
        self.serverip = cf.get("ServerConfig", "serverip")
        self.serverport = cf.get("ServerConfig", "serverport")
        self.VPNserverip = cf.get("ServerConfig", "VPNserverip")
        self.verifyserverip = cf.get("ServerConfig", "verifyserverip")
        #self.forceVPN = cf.get("ServerConfig", "forceVPN")
        self.poweredByTime = cf.get("ServerConfig", "poweredByTime")

      
       