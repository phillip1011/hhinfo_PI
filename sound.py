import os
from datetime import datetime

#要新增語音  RTC更新完成, RTC更新失敗

def spcardCloseTime():
    today=str(datetime.now().strftime('%Y-%m-%d'))
    time=str(datetime.now().strftime('%H%M%S'))
    
    if int(time[2:4])<=30:
        playfile='T'+str(time[0:2])+'30.wav'
    else:
        playfile='T'+str(int(time[0:2])+1)+'00.wav'
    #print('playfile : ' , playfile)
    os.system("aplay wav/"+ playfile)


def sysStartSound():
    print("系統開機",datetime.now())
    os.system("aplay wav/sysStartSound.wav")
def sysLoginSrvSound():
    print("伺服器主機連線成功")
    os.system("aplay wav/sysLoginSrvSound.wav")
def sysLoginSrvFailSound():
    print("伺服器主機連線失敗")
    os.system("aplay wav/sysLoginSrvFailSound.wav")
def sysLoginVpnSound():
    print("VPN伺服器連線成功")
    os.system("aplay wav/sysLoginVpnSound.wav")
def sysLoginVpnFailSound():
    print("VPN伺服器連線失敗")
    os.system("aplay wav/sysLoginVpnFailSound.wav")
def ar721ConnectSound():
    print("AR721讀卡機連線成功")
    os.system("aplay wav/ar721ConnectSound.wav")
def r35cConnectSound():
    print("R35C讀卡機連線成功")
    os.system("aplay wav/r35cConnectSound.wav")
def scannerNotConnect():
    print("讀卡機未連線")
    os.system("aplay wav/scannerNotConnect.wav")
def sysFinishSound():
    print("開機完成",datetime.now())
    os.system("aplay wav/sysFinishSound.wav")
def bootUpdateRetry():
    print("系統時間更新失敗,5分鐘後重試")
    os.system("aplay wav/bootUpdateRetry.wav")
def sysTimeUpdateFinish():
    print("系統時間更新完成")
    os.system("aplay wav/sysTimeUpdateFinish.wav")
def sysTimeUpdateFail():
    print("系統時間更新失敗")
    os.system("aplay wav/sysTimeUpdateFail.wav")
def scannerUpdateTimeFinish():
    print("讀卡機時間更新完成")
    os.system("aplay wav/scannerUpdateTimeFinish.wav")
def scannerUpdateTimeFail():
    print("讀卡機時間更新失敗")
    os.system("aplay wav/scannerUpdateTimeFail.wav")

def scanSuccess():
    os.system("aplay wav/scanSuccess.wav")
def scanail():
    os.system("aplay wav/scanFail.wav")

def spcard():
    os.system("aplay wav/spcard.wav")
def noncard():
    os.system("aplay wav/noncard.wav")
def remote():
    os.system("aplay wav/remote.wav")
def doorOpen():
    os.system("aplay wav/doorOpen.wav")
def doorClose():
    os.system("aplay wav/doorClose.wav")


def spcardOpenDoorSound():
    print("刷卡成功 全區卡,己開門")
    #scanSuccess()
    #spcard()
    doorOpen()
def spcardCloseDoorSound():
    print("刷卡成功 全區卡, 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    #scanSuccess()
    #spcard()
    doorClose()
def openDoorSound():
    print("刷卡成功 一般卡.己開門 ")
    #scanSuccess()
    #noncard()
    doorOpen()
def closeDoorSound():
    print("刷卡成功 一般卡, 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    #scanSuccess()
    #noncard()
    doorClose()
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
    remote()
    doorOpen()
def remoteCloseDoorSound():
    print("遠端操作 鐵卷門關閉中,請注意安全, 請勿任意穿越鐵卷門下方")
    remote()
    doorClose()
def remoteOpenR3Sound():
    print("遠端操作 己開啟電燈電源,請開啟電燈開關")
    remote()
    openR3Sound()
def remoteCloseR3Sound():
    print("遠端操作 己關閉電燈電源")
    remote()
    closeR3Sound()
def remoteOpenR4Sound():
    print("遠端操作 己開啟冷氣電源,請開啟冷氣開關")
    remote()
    openR4Sound()
def remoteCloseR4Sound():
    print("遠端操作 己關閉冷氣電源")
    remote()
    closeR4Sound()


