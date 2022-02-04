import sqlite3
from datetime import datetime
import models.relay as relay

def chkcard(uid):
    #relay.setup()
    #開啟資料庫連線
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c1=conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS cards(id TEXT,customer_id TEXT,card_uuid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_customers(id TEXT,booking_id TEXT,customer_id TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT,aircontrol TEXT)')
    #手動新增記錄   
    # id = '2'  #input cards table
    # customer_id = '3'
    # card_uuid = '3759416887'
    # c.execute("INSERT INTO cards values (?,?,?)", (id,customer_id,card_uuid,))


    # id = '15'    #input booking_customers table
    # booking_id = '184640'
    # customer_id = '2'
    # c.execute("INSERT INTO booking_customers values (?,?,?)", (id,booking_id,customer_id,))


    # id = '184640'    #input booking_customers table
    # deviceid = '329'
    # date = '20220113'
    # range_id = '2300'
    # c.execute("INSERT INTO booking_histories values (?,?,?,?)", (id,deviceid,date,range_id,))

    #查詢記錄----------------------------------------------

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
        print("合法卡號")
        print('customers_id是'+row[1])
        c.execute('select * from spcards where customer_id=?' ,(row[1],))
        i=0
        for row in c:
            print("全區卡")
            i+=1
            if i>=1:
                relay.action(1,5,0)
                if row[2]==3:
                    relay.action(3,255,0)
                break

        c.execute('select * from booking_customers where customer_id=?' ,(row[1],))
        i=0
        for row in c: #先掃看是否有筆數, 如果沒有直接跳出(會掃到多筆)
            i+=1
            print('booking_id:第'+str(i)+'筆'+row[1])
            if i>=1:
                # print("test")
                # print(row[1])
                # print(today)
                # print(range_id)
                c1.execute('select * from booking_histories where id=? and date=? and range_id=?' ,(row[1],today,range_id,))
                xx=0
                
                for row1 in c1: #先掃看是否有筆數, 如果沒有直接跳出(會掃到多筆)
                    print(row1[0])
                    xx+=1
                    if xx>=1:
                        relay.action(1,5,0)
                        relay.action(3,255,0)
                        if row1[4] == '1':
                            relay.action(4,255,0)
                        else:
                            relay.action(4,0,0)
                            print("無預約冷氣資料")
                    else:
                        print("無預約資料")
            else:
                print("not in booking_customers")
    else:
        print("非法卡")

    
    conn.commit()
    conn.close()


if __name__=='__main__':
    uid='4077189990'
    #uid='1234567890'
    chkcard(uid)