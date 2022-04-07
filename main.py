import RPi.GPIO as GPIO
import threading
import serial
import sqlite3
from datetime import datetime
from time import sleep
import WebApiClient.login_internet as login_internet
import models.relay as relay
import WebApiClient.api as api
import WebApiClient.remote as remote


import models.r35c as r35c
import models.ar721 as ar721
import globals 

GPIO.setwarnings(False)


def initGlobals():
    globals.initialize() 


def initRelay():
    relay.setup()
    relay.start_relay()



    

if __name__=='__main__':
    #loop for change relay off
    initGlobals()
    initRelay()


  
   
    #loop for checking internet every 1 min
    # netstatus=1   # 0表示boot時, 1表示每X分鐘檢查
    # t2 = threading.Thread(target=login_internet.main, args=(serverip, VPNserverip,netstatus))
    # t2.start()

    #loop for card number every 1 sec
    
    #input=b'\x7e\x04\x01\x25\xdb\x01'
 
   

    #
    if globals._scanner.name == 'AR721':
        print('Start thread AR721')
        t = threading.Thread(target=ar721.do_read_ar721)
        t.setDaemon(True)
        t.start()
    else:
        print('Start thread R35C')
        t = threading.Thread(target=r35c.do_read_r35c)
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

    #start API flask
    
   
    api.run()
