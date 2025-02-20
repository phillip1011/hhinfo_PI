import os
import pysftp
import globals
from datetime import datetime
from time import sleep
import sound as sound
import subprocess


def get_ovpn_file(sHostName,vpnfile):
    with pysftp.Connection(host=sHostName , username='ovpn', private_key="/home/ubuntu/hhinfo_PI/id_rsa") as sftp:
        # 檔案下載 sftp.get('home\ovpn\遠端檔案位置', '本機檔案位置')
        sftp.get(vpnfile ,"/home/ubuntu/hhinfo_PI/" + vpnfile)

def pingServer(serverip):
    try:
        serverip=str(serverip)
        p = subprocess.check_output(["ping", "-c", "1", serverip])
        print("網頁伺服器連線正常",datetime.now())
        return 0
    except subprocess.CalledProcessError:
        print("網頁伺服器連線失敗",datetime.now())
        return
    

def pingVPNServer(VPNserverip):
    try:
        VPNserverip=str(VPNserverip)
        p = subprocess.check_output(["ping", "-c", "1", VPNserverip])
        print("VPN伺服器連線正常",datetime.now())
        return 0
    except subprocess.CalledProcessError:
        print("VPN伺服器連線失敗",datetime.now())
        return

def main(keepalive):
    # print(serverip)
    # print(VPNserverip)
    while True:
        if pingServer(globals._server.serverip) ==0:    #PING WEB SRV
            if keepalive==False:
                sound.sysLoginSrvSound()
            if pingVPNServer(globals._server.VPNserverip) !=0:     #PING  VPN SRV
                print("PING "+globals._server.VPNserverip+" 嘗試登入VPN主機")
                mac=open('/sys/class/net/eth0/address').readline()
                mac=mac[0:17]
                vpnfile = str(mac.replace(":",""))
                vpnfile = vpnfile+".ovpn"
                if os.path.isfile(vpnfile) and os.path.getsize(vpnfile) != 0:
                    #wlog("VPN登入檔案存在, 準備登錄VPN Server","a+")
                    print("VPN登入檔案存在, 準備登錄VPN Server")
                else:
                    wlog("下載VPN登入檔案中,請等待","a+")
                    try:
                        get_ovpn_file(globals._server.serverip,vpnfile)
                        wlog("下載VPN登入檔案,完成! , 準備登錄VPN Server","a+")
                    except:
                        if os.path.getsize(vpnfile) == 0:      #因為FTP失敗仍會產生檔案名稱,故在此判斷刪除檔案
                            os.system("rm " + vpnfile )                        
                            wlog("下載VPN登入檔案失敗!","a+")
                os.system("sudo killall openvpn")
                sleep(1)
                os.system("sudo -b openvpn --config /home/ubuntu/hhinfo_PI/" +vpnfile)
                sleep(10)
                if pingVPNServer(globals._server.VPNserverip) ==0:
                    wlog("登入VPN成功","a+")
                    if keepalive==False:
                        sound.sysLoginVpnSound()
                else:
                    wlog("登入VPN失敗","a+")

        else:
            os.system("sudo killall openvpn") #防止不正常斷線, VPN卡Threading
            if keepalive==False:
                sound.sysLoginSrvFailSound()
        if keepalive==True:
            sleep(60*1)
        else:
            return
    
def wlog(msg,fnc):
    #將結果寫到start_log.txt
    print(msg)
    timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    text_file = open("/home/ubuntu/hhinfo_PI/start_log.txt", fnc)
    text_file.write(timenow+" "+msg+'\n')
    text_file.close()




   