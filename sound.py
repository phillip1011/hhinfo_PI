import os
#import globals

def sysStartSound():
    print("系統開機")
    os.system("aplay wav/sysStartSound.wav")
def sysLoginSrvSound():
    print("伺服器主機連線成功")
    os.system("aplay wav/sysLoginSrvSound.wav")
def sysLoginVpnSound():
    print("VPN伺服器連線成功")
    os.system("aplay wav/sysLoginVpnSound.wav")
    #sleep(10)
def sysScannerSound(_scanner):
    if _scanner=='AR721':
        print("AR721讀卡機連線成功")
        os.system("aplay wav/ar721ConnectSound.wav")
    elif _scanner=='R35C':
        print("R35C讀卡機連線成功")
        os.system("aplay wav/r35cConnectSound.wav")
    else:
        print("讀卡機未連線")
        os.system("aplay wav/scannerNotConnect.wav")
def sysFinishSound():
    print("開機完成")
    os.system("aplay wav/sysFinishSound.wav")


def spcardOpenDoorSound():
    print("刷卡成功 全區卡,己開門 臨時供電到 (48組時間")
    os.system("aplay wav/spcardOpenDoorSound.wav")
def spcardCloseDoorSound():
    print("刷卡成功 全區卡, 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    os.system("aplay wav/spcardCloseDoorSound.wav")
def openDoorSound():
    print("刷卡成功 一般卡.己開門 ")
    os.system("aplay wav/openDoorSound.wav")
def closeDoorSound():
    print("刷卡成功 一般卡, 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    os.system("aplay wav/closeDoorSound.wav")
def nonAuthCard():
    print("您的卡號不在租借時間內,請確認您的租借時間或請冾區公所詢問")
    os.system("aplay wav/nonAuthCard.wav")
def nonRegisterCard():
    print("您的卡號沒有登錄在租借系統內,請冾區公所辦理租借手續")
    os.system("aplay wav/nonRegisterCard.wav")


def openR3Sound():
    print("己開啟電燈電源,請開啟電燈開關")
    os.system("aplay wav/openR3Sound.wav")
def closeR3Sound():
    print("己關閉電燈電源")
    os.system("aplay wav/closeR3Sound.wav")
def openR4Sound():
    print("己開啟冷氣電源,請開啟冷氣開關 ")
    os.system("aplay wav/openR4Sound.wav")
def closeR4Sound():
    print("己關閉冷氣電源")
    os.system("aplay wav/closeR4Sound.wav")


def remoteOpenDoorSound():
    print("遠端操作 己開門")
    os.system("aplay wav/remoteOpenDoorSound.wav")
def remoteCloseDoorSound():
    print("遠端操作 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    os.system("aplay wav/remoteCloseDoorSound.wav")
def remoteOpenR3Sound():
    print("遠端操作 己開啟電燈電源,請開啟電燈開關,臨時供電到 (48組時間")
    os.system("aplay wav/remoteOpenR3Sound.wav")
def remoteCloseR3Sound():
    print("遠端操作 己關閉電燈電源")
    os.system("aplay wav/remoteCloseR3Sound.wav")
def remoteOpenR4Sound():
    print("遠端操作 己開啟冷氣電源,請開啟電燈開關,臨時供電到 (48組時間")
    os.system("aplay wav/remoteOpenR4Sound.wav")
def remoteCloseR4Sound():
    print("遠端操作 己關閉冷氣電源")
    os.system("aplay wav/remoteCloseR4Sound.wav")


