#watchdog.py
import os
import requests
from time import sleep
from getmac import get_mac_address
import socket
import pysftp

def getmac():

    try:
        mac = open('/sys/class/net/eth0/address').readline()
    except:
        mac = "00:00:00:00:00:00"

    return mac[0:17]



def getlocalip():
    serverip= "35.221.198.141"  #hhremote.com主機
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((serverip, 80))
        print(s.getsockname()[0])
        ip = str(s.getsockname()[0])   #取得Local ip
        s.close()
        return ip
    except: 
        return ""

def checkFlask1():
    controlip = getlocalip()
    if controlip == "" : return 
    headers = {'Content-Type': 'application/json','token':'aGhpbmZvOjIwMjAwMTE2MjIxMDM5'}
    try :
        api_url_base = "http://" + controlip + ":4661/api/v3/remote/control/time"
        response = requests.get(api_url_base, headers=headers, verify=False,timeout=15)
        print (response.status_code)
        if (response.status_code == 200):
            #nothing 
            print("websit1 is up")
    except :
        print ("start web sit")
        os.system("sudo python3 /home/ubuntu/nfc/main.py > main.log 2&1 &")
        os.system("sudo aplay /home/ubuntu/nfc/mp3/Start_App.wav")


def checkFlask2():
    controlip = getlocalip()
    if controlip == "" : return
    headers = {'Content-Type': 'application/json','token':'aGhpbmZvOjIwMjAwMTE2MjIxMDM5'}
    try :
        api_url_base = "http://" + controlip + ":4663/api/v3/remote/control/time"
        response = requests.get(api_url_base, headers=headers, verify=False,timeout=15)
        print (response.status_code)
        if (response.status_code == 200):
            #nothing
            print("websit2 is up")
    except :
        print ("start web sit")

        os.system("sudo python3 /home/ubuntu/nfc1/main.py > main1.log 2&1 &")
        os.system("sudo aplay /home/ubuntu/nfc/mp3/Start_App.wav")


def get_ovpn_file(filename):
    sPassWord='aGhpbmZvOjIwMjAwMTE2MjIxMDM5'
    sHostName = '35.221.198.141'
    sUserName = 'ovpn'
    #cnopts = pysftp.CnOpts();
    #knownhosts='known_hosts')
    #cnopts.hostkeys = None
    #cnopts.hostkeys.load('/home/ubuntu/.ssh/know_hosts')
    #cnopts = pysftp.CnOpts()
    #cnopts.hostkeys = None 
    with pysftp.Connection(host=sHostName , username=sUserName, private_key="/home/ubuntu/nfc/id_rsa") as sftp:
    #with pysftp.Connection(sHostName, username=sUserName, password=sPassWord, cnopts=cnopts) as sftp:
        print(filename)
        # 檔案下載 sftp.get('遠端檔案位置', '本機檔案位置')
        sftp.get(filename ,"/home/ubuntu/nfc/" + filename)
        #sftp.close()


def check_file():
    mac = getmac() 
    #mac = get_mac_address()
    
    print(str(mac))
    mac = mac.replace(":","")
    if (mac == "0000000000000"):
        return 

    filepath= mac
    if os.path.isfile(filepath):
        return
    else:
        f = open (filepath,"x")
        f.close()
        print("put file")
        sPassWord='aGhpbmZvOjIwMjAwMTE2MjIxMDM5'
        sHostName = '35.221.198.141'
        sUserName = 'ovpn'
        #cnopts = pysftp.CnOpts();
        #cnopts.hostkeys = None


        with pysftp.Connection(host=sHostName , username=sUserName, private_key="/home/ubuntu/nfc/id_rsa") as sftp:
        #with pysftp.Connection(sHostName, username=sUserName, password=sPassWord, cnopts=cnopts) as sftp:
            print(filepath)
            # 檔案下載 sftp.get('遠端檔案位置', '本機檔案位置')
            
            sftp.put(filepath,'./mac_address/' + filepath)
            #sftp.close()
def pingServer():
    VpnServer = "35.221.198.141"
    response_s = os.system("ping -c 1 " + VpnServer)
    if response_s != 0:
        print(response_s)
        response_s = os.system("ping -c 1 " + VpnServer)
        if response_s != 0:
            return 1
        else: 
            return 0
    else:
        print(response_s)
        return 0

def pingVpnServer():
    VpnServer = "10.8.0.1"
    response = os.system("ping -c 1 " + VpnServer)
    if response != 0:
        response_s = os.system("ping -c 1 " + VpnServer)
        if response_s != 0:
            return 1
        else:
            return 0
    else:
        return 0
                                                                            


#程式開始-----------------------------------------------------------------------------------------------
#define user name password
#check_file()
#os.system("sudo aplay /home/ubuntu/nfc/mp3/wakeup.wav")
hostname = "10.8.0.1"
#response = os.system("ping -c 1 " + hostname)
vpnactive = 0
#while vpnactive < 5 :
if pingServer()  == 0:  #如果等於0表示網路有通,SERVER有回應
    if pingVpnServer() == 0:  #如果等於0表示已連上VPN SERVER,且網路有通VPN SERVER
        pingstatus = "Network Active"
        checkFlask1()
        checkFlask2()
        #vpnactive =6
    else:
        check_file()
        try:
            print("stop vpn")
            #os.system ("sudo poff pptpd")
            os.system ("sudo killall openvpn")   
        except:
            print("no vpn process")
        mac = getmac()
        mac = mac.replace(":","")
        filepath= mac +".ovpn"
        if (mac != "0000000000000"):
            get_ovpn_file(filepath)
        os.system("sudo -b openvpn --config /home/ubuntu/nfc/" +filepath)
        os.system("sudo aplay /home/ubuntu/nfc/mp3/Login_Vpn.wav")
        os.system("sudo aplay /home/ubuntu/nfc/mp3/Wait.wav")
        sleep(10)
        if(pingVpnServer() ==0):
            checkFlask1()
            checkFlask2()

else:
    try:
        print("stop vpn")
        os.system ("sudo killall openvpn")
    except:
        print("no vpn process")
    os.system("sudo aplay /home/ubuntu/nfc/mp3/Find_Server.wav")
#os.system("sudo aplay /home/ubuntu/nfc/mp3/wakeup.wav")

