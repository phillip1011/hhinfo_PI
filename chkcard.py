import sqlite3
from datetime import datetime
import models.relay as relay
import WebApiClent.remote as remote

def chkcard(uid):
    #relay.setup()
    #開啟資料庫連線

    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c2=conn.cursor()
    c1=conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS cards(id TEXT,customer_id TEXT,card_uuid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_customers(id TEXT,booking_id TEXT,customer_id TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT,aircontrol TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS scanlog(cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT,auth TEXT,process TEXT)')    
    
    auth=""
    process=""

    today=str(datetime.now().strftime('%Y-%m-%d'))
    time=str(datetime.now().strftime('%H:%M:%S'))
    #10:15:08 (HH:MM:SS)
    if int(time[3:5])>=30:
        range_id=str(time[0:2])+':30'
        print('系統時段=',range_id)
    else:
        range_id=str(time[0:2])+':00'
        print('系統時段=',range_id)

    c.execute('select * from cards where card_uuid=?' ,(uid,)) #找尋資料庫中, 是否有合法之卡號
    i=0
    for row in c: #資料庫筆數如果為0則表示無此卡號
        i+=1
    if i>=1:
        auth="合法卡"
        # print("合法卡號")
        # print('customers_id是'+row[1])
        sxstatus = relay.read_sensor()
        sensor0=sxstatus[0]

        c2.execute('select * from spcards where customer_id=?' ,(row[1],))
        i=0
        for row2 in c2:
            i+=1
            if i>=1:
                spauth=row2[1]
                if sensor0==1:  #S0=1 表示門狀態是關閉
                    process="全區卡-開門"
                    relay.action(1,5,0)
                    spauth=row2[2]
                    # print(spauth)
                    if spauth=="":
                        print("無其他授權")
                    elif spauth=="3,4":
                        print("開燈開AC")
                        relay.action(3,255,0)
                        relay.action(4,255,0)
                    elif spauth[0]==str(3):
                        print("開燈")
                        relay.action(3,255,0)
                    elif spauth[0]==str(4):
                        print("開AC")
                        relay.action(4,255,0)
                else:
                    process="全區卡-關門"
                    relay.action(2,5,0)
                    relay.action(3,0,0)
                    relay.action(4,0,0)
                break
        if process=="":
            print('chkpoint')
            process="非預約時段"
            c.execute('select * from booking_customers where customer_id=?' ,(row[1],))
            i=0
            for row in c: #找尋booking_customers資料庫中, 是否有此客戶
                i+=1
                print('booking_id:第'+str(i)+'筆'+row[1])
                if i>=1:
                    # print("test")
                    # print(row[1])
                    # print(today)
                    # print(range_id)
                    c1.execute('select * from booking_histories where id=? and date=? and range_id=?' ,(row[1],today,range_id,))
                    xx=0
                    for row1 in c1: #找尋booking_histories資料庫中, 是否有此客戶的預約
                        print(row1[0])
                        xx+=1
                        if xx>=1:
                            process="租借時段-開門"
                            relay.action(1,5,0)
                            relay.action(3,255,0)
                            if row1[4] == '1':
                                relay.action(4,255,0)
                            else:
                                relay.action(4,0,0)
    else:
        auth="非法卡"
        process="禁止進入"


    c.execute("INSERT INTO scanlog VALUES(?,?,?,0,?,?)", (uid,today,time,auth,process,))
    conn.commit()
    conn.close()

if __name__=='__main__':
    uid='4077189990'
    #uid='1234567890'
    chkcard(uid)