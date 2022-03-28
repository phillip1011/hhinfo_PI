import configparser
class ServerModel:
    token = ''
    token_key = ''
    serverip = ''
    serverport = ''
    VPNserverip = ''
  
 
  
    def __init__(self):
        print("_________ServerModel run________init_________")
        cf = configparser.ConfigParser()
        cf.read("config.ini")
        self.token = cf.get("ServerConfig", "token")
        self.token_key = cf.get("ServerConfig", "token_key")
        self.serverip = cf.get("ServerConfig", "serverip")
        self.serverport = cf.get("ServerConfig", "serverport")
        self.VPNserverip = cf.get("ServerConfig", "VPNserverip")
       
    
    def show(self):
        print("ServerModel show")
        print("token = " + self.token)
        print("token_key = " + self.token_key)
        print("serverip = " + self.serverip)
        print("serverport = " + self.serverport)
        print("VPNserverip = " + self.VPNserverip)
      
       