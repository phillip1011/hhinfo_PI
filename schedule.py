import sqlite3
from datetime import datetime
import globals
rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
controlip=""




def initGlobals():
    globals.initialize() 
    globals._relay.setupGPIO()


def chkcard():
    #globals._relay.setup()
    #開啟資料庫連線
    
    if globals._device.mode =='手動':
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
    c.execute('select * from booking_histories where date=? and range_id=? order by aircontrol desc' ,(today,range_id,))
    data = c.fetchone()

    if data == None:
        print("本時段無預約:關閉R3及R4")
        globals._relay.action(3,0,0)
        globals._relay.action(4,0,0)
        return 0
    
   
    print("本時段有預約")
    if data[4] == '0':
            print("無預約冷氣:關閉R4")
            globals._relay.action(4,0,0)
 

    conn.commit()
    conn.close()


if __name__=='__main__':
    initGlobals()
    chkcard()