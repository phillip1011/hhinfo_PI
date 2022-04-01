import sqlite3
from datetime import datetime
import models.relay as relay
import WebApiClient.remote as remote

rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
controlip=""


from models.DeviceModel import DeviceModel
from models.ServerModel import ServerModel
from models.ScannerModel import ScannerModel



def initServer():
    global _server
    _server = ServerModel()
  



def initScanner():
    global _scanner
    _scanner = ScannerModel()

def initDevice():
    global _device
    _device = DeviceModel()
    




def chkcard():
    #relay.setup()
    #開啟資料庫連線
    

    if _device.mode =='手動':
        return 0

    
    today=str(datetime.now().strftime('%Y%m%d'))
    time=str(datetime.now().strftime('%H%M%S'))
       
    if int(time[2:4])>=30:
        range_id=str(time[0:2])+'30'
        print(range_id)
    else:
        range_id=str(time[0:2])+'00'
        print(range_id)

    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from booking_histories where date=? and range_id=?' ,(today,range_id,))
   
    i=0
    for row in c: #先掃看是否有預約, 如果沒有直接關閉R3R4
        i+=1
    print('本時段預約人數',i)
    if i>=1:
        print("本時段有預約:",range_id)
        # relay.action(3,255,0)
        if row[4] == '0':
            print("本時段無預約冷氣:關閉R4")
            relay.action(4,0,0)
    else:
        print("本時段無預約:關閉R3及R4")
        relay.action(3,0,0)
        relay.action(4,0,0)
    

    sxstatus = relay.read_sensor()
    rxstatus = relay.relaystatus

    remote.scode(_device.localip,rxstatus,sxstatus)
    conn.commit()
    conn.close()


if __name__=='__main__':
    initServer()
    initScanner()
    initDevice()
    remote._server = _server
    remote._device = _device
    #uid='4077189990'
    #uid='1234567890'
    chkcard()