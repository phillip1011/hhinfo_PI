import sqlite3
from datetime import datetime
import models.relay as relay



def chkcard():
    #relay.setup()
    #開啟資料庫連線
    conn=sqlite3.connect("/home/ubuntu/nfc/cardno.db")
    c=conn.cursor()
    #c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT)')

    today=str(datetime.now().strftime('%Y%m%d'))
    time=str(datetime.now().strftime('%H%M%S'))
    print(today)
    print(time)
    if int(time[2:4])>=30:
        range_id=str(time[0:2])+'30'
        print(range_id)
    else:
        range_id=str(time[0:2])+'00'
        print(range_id)

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
    
    conn.commit()
    conn.close()


if __name__=='__main__':
    #uid='4077189990'
    #uid='1234567890'
    chkcard()