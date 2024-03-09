#!/usr/bin/python3
import RPi.GPIO as GPIO
import threading
import serial
#import WebApiClient.login_internet as login_internet
import WebApiClient.api as api
import WebApiClient.remote as remote
import WebApiClient.updatetime as updatetime
import upload    
import models.r35c as r35c
import models.ar721 as ar721
import models.AR837TCP as ar837
import globals 
import sound as sound

GPIO.setwarnings(False)


def initGlobals():
    globals.initialize()
    globals._relay.setupGPIOandInit()




if __name__=='__main__':
    #loop for change relay off
    initGlobals()

    # if globals._server.forceVPN == 'true':
    #     print('強制啟用VPN')
    #     tVPN = threading.Thread(target=login_internet.main, args=(True,))
    #     tVPN.setDaemon(True)
    #     tVPN.start()
     
    if globals._scanner.scannerName == 'AR721':
        print('Start thread AR721')
        sound.ar721ConnectSound()
        t = threading.Thread(target=ar721.do_read_ar721)
        t.setDaemon(True)
        t.start()
    elif globals._scanner.scannerName =='AR837' :
        print('Start thread AR837')
        #sound.r35cConnectSound()
        t = threading.Thread(target=ar837.do_read_ar837)
        t.setDaemon(True)
        t.start()
    elif globals._scanner.scannerName =='R35C' :
        print('Start thread R35C')
        sound.r35cConnectSound()
        t = threading.Thread(target=r35c.do_read_r35c)
        t.setDaemon(True)
        t.start()
    elif globals._scanner.scannerName =='None' :
        print('no scanner found')
        sound.scannerNotConnect()

    #auto update system time each 10 mins
    if globals._RTC.timeUpdate=='fail':
        tTime = threading.Thread(target=updatetime.autoUpdateTime)
        tTime.setDaemon(True)
        tTime.start()

    #loop for report
    t3 = threading.Thread(target=remote.report)
    t3.setDaemon(True)
    t3.start()

    #loop for sensor change
    t4 = threading.Thread(target=remote.monitor_sensor)
    t4.setDaemon(True)
    t4.start()

    #loog for upload log
    t5 = threading.Thread(target=upload.uploadlog)
    t5.setDaemon(True)
    t5.start()

    #start API flask
    
    sound.sysFinishSound()
    api.run()
    
