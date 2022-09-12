import sqlite3
from datetime import datetime
import globals
rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
controlip=""




def initGlobals():
    globals.initRelay()
    globals.initDevice()
    globals._relay.setupGPIO()
    globals.initScanner()

def chkcard():
    if globals._device.mode =='手動':
        print('手動模式, 不關閉Relay')
        return 0
    if globals._device.style =='公用' and globals._device.is_booking =='0':
        print('不可預約公用門, 不檢查Relay')
        return 0

    today=str(datetime.now().strftime('%Y-%m-%d'))
    time=str(datetime.now().strftime('%H%M%S'))
  
    if int(time[2:4])>=30:
        range_id=str(time[0:2])+':30'
    else:
        range_id=str(time[0:2])+':00'

    print('Todate : ' , today)
    print('Range_id : ' , range_id)

    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from booking_histories where date=? and range_id=? and deviceid=? order by aircontrol desc' ,(today,range_id,globals._device.dev_id,))
    data = c.fetchone()

    if data == None:
        print("本時段無預約:關閉R3及R4")
        globals._relay.action(3,0,0)
        globals._relay.action(4,0,0)
        return 0
    
    else:
        if globals._server.poweredByTime == true:
            print("本時段有預約:開啟R3並檢查是否開啟R4")
            globals._relay.action(3,255,0)
            if data[4] == '1':
                print("有預約冷氣:開啟R4")
                globals._relay.action(4,255,0)
    if data[4] == '0':  #不管是時間送電還是刷卡送電,只要沒預約都斷冷氣電源
        print("無預約冷氣:關閉R4")
        globals._relay.action(4,0,0)  

    conn.commit()
    conn.close()


if __name__=='__main__':
    initGlobals()
    chkcard()