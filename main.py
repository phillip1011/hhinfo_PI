#!/usr/bin/python3
import RPi.GPIO as GPIO
import threading
import serial
import WebApiClient.login_internet as login_internet
import WebApiClient.api as api
import WebApiClient.remote as remote

import upload    
import models.r35c as r35c
import models.ar721 as ar721
import globals 

GPIO.setwarnings(False)


def initGlobals():
    globals.initialize() 
    globals._relay.setupGPIOandInit()




    

if __name__=='__main__':
    #loop for change relay off
    initGlobals()

    if globals._server.forceVPN == 'true':
        print('強制啟用VPN')
        t = threading.Thread(target=login_internet.main, args=(True,))
        t.setDaemon(True)
        t.start()
     
   
    
    t = threading.Thread(target=globals._scanner.doRead)
    t.setDaemon(True)
    t.start()

 

   
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
    
   
    api.run()
