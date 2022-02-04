import os
import socket
import pysftp
from datetime import datetime
from time import sleep

def get_ovpn_file(sHostName,vpnfile):
    with pysftp.Connection(host=sHostName , username='ovpn', private_key="/home/ubuntu/nfc/id_rsa") as sftp:
        # 檔案下載 sftp.get('遠端檔案位置', '本機檔案位置')
        sftp.get(vpnfile ,"/home/ubuntu/nfc/" + vpnfile)


def pingServer(serverip):
    response_s = os.system("ping -c 1 " + serverip)
    if response_s == 0:
        return response_s
    else:
        return response_s

def pingVPNServer(VPNserverip):
    response_s = os.system("ping -c 1 " + VPNserverip)
    if response_s == 0:
        return response_s
    else:
        return response_s

def main(serverip,VPNserverip):
    # print(serverip)
    # print(VPNserverip)
    while True:
        if pingServer(serverip) ==0:    #PING WEB SRV
            #wlog("PING "+serverip+" WEB主機回應成功","w+")
            print("PING "+serverip+" WEB主機回應成功")
            if pingVPNServer(VPNserverip) ==0:     #PING  VPN SRV
                #wlog("PING "+VPNserverip+" VPN主機回應成功","a+")
                print("PING "+VPNserverip+" VPN主機回應成功")
            else:
                #wlog("PING "+VPNserverip+" 嘗試登入VPN主機","a+")
                print("PING "+VPNserverip+" 嘗試登入VPN主機")
                mac=open('/sys/class/net/eth0/address').readline()
                mac=mac[0:17]
                vpnfile = str(mac.replace(":",""))
                vpnfile = vpnfile+".ovpn"
                if os.path.isfile(vpnfile):
                    #wlog("VPN登入檔案存在, 準備登錄VPN Server","a+")
                    print("VPN登入檔案存在, 準備登錄VPN Server")
                else:
                    wlog("下載VPN登入檔案中,請等待","a+")
                    get_ovpn_file(serverip,vpnfile)
                    wlog("下載VPN登入檔案,完成! , 準備登錄VPN Server","a+")
                os.system("sudo killall openvpn")
                sleep(1)
                os.system("sudo -b openvpn --config /home/ubuntu/nfc/" +vpnfile)
                sleep(10)
                if pingVPNServer(VPNserverip) ==0:
                    wlog("登入VPN成功","a+")
                else:
                    wlog("登入VPN失敗","a+")

        else:
            os.system("sudo killall openvpn") #防止不正常斷線, VPN卡Threading
            #wlog("PING "+serverip+" WEB主機回應失敗----結束","a+")
            print("PING "+serverip+" WEB主機回應失敗----結束")
        sleep(60*1)
    
def wlog(msg,fnc):
    #將結果寫到start_log.txt
    timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    text_file = open("/home/ubuntu/nfc/start_log.txt", fnc)
    text_file.write(timenow+" "+msg+'\n')
    text_file.close()

if __name__=='__main__':
    serverip= "35.221.198.141"
    VPNserverip = "10.8.0.1"    
    #sleep(1)
    main(serverip,VPNserverip)
