import sqlite3
from models.DeviceModel import DeviceModel
from models.ServerModel import ServerModel
from models.ScannerModel import ScannerModel
from models.RelayModel import RelayModel
from models.RTCModel import RTCModel
from datetime import datetime, timedelta


def initializeWithOutGPIO():
    initDatabase()
    initDevice()
    initServer()
    #initScanner()
    #removeOldScannerLog()
    #initRTC()

    
def initialize(): 
    initRelay()
    initDatabase()
    initDevice()
    initServer()
    initScanner()
    removeOldScannerLog()
    initRTC()

def initDatabase():
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS device ('
              'id TEXT,'
              'ip TEXT,'
              'local_ip TEXT,'
              'ip_mode TEXT,'
              'family TEXT,'
              'name TEXT,'
              'description TEXT,'
              'group_id TEXT,'
              'mode TEXT,'
              'style TEXT,'
              'type TEXT,'
              'is_booking TEXT,'
              'status TEXT,'
              'kernel TEXT,'
              'buffer_minutes TEXT,'
              'delay_minutes TEXT,'
              'spcard_minutes TEXT)'
            )
    c.execute('CREATE TABLE IF NOT EXISTS spcards (id TEXT,customer_id TEXT,authority TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS cards (id TEXT,customer_id TEXT,card_uuid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_customers (id TEXT,booking_id TEXT,customer_id TEXT,source TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_histories (id TEXT,deviceid TEXT,date TEXT,range_id TEXT,aircontrol TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS scanlog (cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT,auth TEXT,process TEXT,result TEXT)') 
    c.execute('CREATE TABLE IF NOT EXISTS spcard_time (cardnbr TEXT,start_time TEXT,end_time TEXT,authority TEXT)')  
    conn.close()


def initServer():
    global _server
    _server = ServerModel()
  

def initScanner():
    global _scanner
    _scanner = ScannerModel()

def initDevice():
    global _device
    _device = DeviceModel()

def initRelay():
    global _relay
    _relay = RelayModel()

def removeOldScannerLog():
    sub_7_date = str((datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('Delete from scanlog where date <= ? ',(sub_7_date,))
    conn.commit()
    conn.close()

def initRTC():  
    global _RTC
    _RTC = RTCModel()