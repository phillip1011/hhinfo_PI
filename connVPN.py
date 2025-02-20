#!/usr/bin/python3
import os
import pysftp
from datetime import datetime
from time import sleep
import sound as sound
import subprocess
import configparser

def get_ovpn_file(sHostName,vpnfile):
    with pysftp.Connection(host=sHostName , username='ovpn', private_key="/home/ubuntu/hhinfo_PI/id_rsa") as sftp:
        # 檔案下載 sftp.get('home\ovpn\遠端檔案位置', '本機檔案位置')
        sftp.get(vpnfile ,"/home/ubuntu/hhinfo_PI/" + vpnfile)
        
def pingServer(serverip):
    try:
        serverip=str(serverip)
        p = subprocess.check_output(["ping", "-c", "1", serverip])
        #print("網頁伺服器連線正常",datetime.now())
        return 0
    except subprocess.CalledProcessError:
        print("網頁伺服器連線失敗",datetime.now())
        return
def pingVPNServer(VPNserverip):
    # 先從tun0 , 抓取ip , 
    # 有Tun0時,output=IP,
    # 無Tun0時,output=Device "tun0" does not exist.
    cmd = "/sbin/ip -o -4 addr list tun0 | awk '{print $4}' | cut -d/ -f1"
    output = subprocess.getoutput(cmd)
    if "not exist" not in output: 
        #print("VPN伺服器連線正常",datetime.now())
        return 0
    else:
        print("VPN伺服器連線失敗",datetime.now())
        return
    # try:
    #     VPNserverip=str(VPNserverip)
    #     p = subprocess.check_output(["ping", "-c", "1", VPNserverip])
    #     print("VPN伺服器連線正常",datetime.now())
    #     return 0
    # except subprocess.CalledProcessError:
    #     print("VPN伺服器連線失敗",datetime.now())
    #     return
def wlog(msg,fnc):
    #將結果寫到start_log.txt
    print(msg)
    timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    text_file = open("/home/ubuntu/hhinfo_PI/start_log.txt", fnc)
    text_file.write(timenow+" "+msg+'\n')
    text_file.close()

def chkFile():
    if os.path.isfile(vpnfile) and os.path.getsize(vpnfile) != 0:
        print("VPN登入檔案存在, 準備登入VPN Server")
    else:
        try:
            get_ovpn_file(serverip,vpnfile)
            wlog("下載VPN登入檔案,完成! , 準備登入VPN Server","a+")
        except:
            if os.path.getsize(vpnfile) == 0:      #因為FTP失敗仍會產生檔案名稱,故在此判斷刪除檔案
                os.system("rm " + vpnfile )                        
                wlog("下載VPN登入檔案失敗!","a+")

def connVPN():
    if pingVPNServer(VPNserverip) !=0:
        os.system("sudo killall openvpn")
        sleep(1)
        os.system("sudo -b openvpn --config /home/ubuntu/hhinfo_PI/" +vpnfile)
        sleep(8)
        if pingVPNServer(VPNserverip) ==0:
            wlog("登入VPN","a+")
            sound.sysLoginVpnSound()

if __name__=='__main__':
    cf = configparser.ConfigParser()
    cf.read("/home/ubuntu/hhinfo_PI/config.ini")
    serverip = cf.get("ServerConfig", "serverip")
    VPNserverip = cf.get("ServerConfig", "VPNserverip")
    try:
        mac=open('/sys/class/net/eth0/address').readline()
    except:
        mac=open('/sys/class/net/wlan0/address').readline()
    mac=mac[0:17]
    vpnfile = str(mac.replace(":",""))+".ovpn"
    os.system("amixer -c 0 set Headphone 90%")  #調整系統音量到90%


    while True :
        if pingServer(serverip)==0:
            if pingVPNServer(VPNserverip) !=0:
                chkFile()
                connVPN()
        else:
            os.system("sudo killall openvpn")
            sleep(1)
            
        sleep(60)
