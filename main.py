import RPi.GPIO as GPIO
import threading
import serial
import sqlite3
from datetime import datetime
from time import sleep
import WebApiClent.login_internet as login_internet
import models.relay as relay
import WebApiClent.api as api
import WebApiClent.remote as remote


import models.r35c as r35c
import models.ar721 as ar721

from models.DeviceModel import DeviceModel
from models.ServerModel import ServerModel
from models.ScannerModel import ScannerModel


GPIO.setwarnings(False)
global uid

def initServer():
    global _server
    _server = ServerModel()
  

def initRelay():
    relay.setup()
    relay.start_relay()

def initScanner():
    global _scanner
    _scanner = ScannerModel()

def initDevice():
    global _device
    _device = DeviceModel()
    

if __name__=='__main__':
    #loop for change relay off
    initDevice()
    initServer()
    initRelay()
    initScanner()

  
    print(_server)
    print(_device)
    print(_scanner)
    #loop for checking internet every 1 min
    # netstatus=1   # 0表示boot時, 1表示每X分鐘檢查
    # t2 = threading.Thread(target=login_internet.main, args=(serverip, VPNserverip,netstatus))
    # t2.start()

    #loop for card number every 1 sec
    
    #input=b'\x7e\x04\x01\x25\xdb\x01'
 
   

    #
    if _scanner.name == 'AR721':
        print('Start thread AR721')
        t = threading.Thread(target=ar721.do_read_ar721, args=(_scanner,_device))
        t.setDaemon(True)
        t.start()
    else:
        print('Start thread R35C')
        t = threading.Thread(target=r35c.do_read_r35c, args=(_scanner,_device))
        t.setDaemon(True)
        t.start()
    
 

   
    #loop for report every 3 min
    remote._server = _server
    remote._device = _device
    
    

    t3 = threading.Thread(target=remote.report, args=(_server,_device))
    t3.setDaemon(True)
    t3.start()

    #loop for sensor change every 0.1 sec
    t4 = threading.Thread(target=remote.monitor_sensor, args=(_server,_device))
    t4.setDaemon(True)
    t4.start()

    #start API flask
    # api._server  = _server
    # api._device = _device
    # api.port = 4661
    # api.token_key=token_key
    # api.sname=sname
    # api.baurate=baurate
    # api.controlname=controlname
    # api.doortype=doortype
    api._server = _server
    api._device = _device
    api._scanner = _scanner
    api.run()
