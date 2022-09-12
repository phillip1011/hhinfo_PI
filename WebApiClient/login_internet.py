import os
import pysftp
import globals
from datetime import datetime
from time import sleep
import sound as sound


def get_ovpn_file(sHostName,vpnfile):
    with pysftp.Connection(host=sHostName , username='ovpn', private_key="/home/ubuntu/hhinfo_PI/id_rsa") as sftp:
        # 檔案下載 sftp.get('home\ovpn\遠端檔案位置', '本機檔案位置')
        sftp.get(vpnfile ,"/home/ubuntu/hhinfo_PI/" + vpnfile)

def pingServer(serverip):
    response_s = os.system("ping -c 1 " + serverip)
    if response_s == 0:
        return response_s
    else:
        return response_s

def pingVPNServer(VPNserverip):
    response_s = os.system("ping -c 1 " + VPNserverip)
    if response_s == 0:
        response_s=os.system("ip addr |grep tun0")
        return response_s
    else:
        return response_s

def main(keepalive):
    # print(serverip)
    # print(VPNserverip)
    while True:
        if pingServer(globals._server.serverip) ==0:    #PING WEB SRV
            #wlog("PING "+serverip+" WEB主機回應成功","w+")
            print("PING "+globals._server.serverip+" WEB主機回應成功")
            if keepalive==False:
                sound.sysLoginSrvSound()
            if pingVPNServer(globals._server.VPNserverip) ==0:     #PING  VPN SRV
                #wlog("PING "+VPNserverip+" VPN主機回應成功","a+")
                print("PING "+globals._server.VPNserverip+" VPN主機回應成功")
            else:
                #wlog("PING "+VPNserverip+" 嘗試登入VPN主機","a+")
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
            #wlog("PING "+serverip+" WEB主機回應失敗----結束","a+")
            print("PING "+globals._server.serverip+" WEB主機回應失敗----結束")
            if keepalive==False:
                sound.sysLoginSrvFailSound()
        globals.initDevice()
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




   