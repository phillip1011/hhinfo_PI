import sqlite3
from datetime import datetime
import models.relay as relay
import WebApiClent.remote as remote
from time import sleep
import serial
from upload import uploadlog
def ar721comm(node,func,data):
    xor=255^node^int(func,16)^int(data,16)
    sum=node+int(func,16)+int(data,16)+xor
    sum =sum % 256
    # print('xor=',hex(xor))
    # print('sum=',hex(sum))
    comm=b'\x7e\x05'+ bytes([node])+ bytes([int(func,16)])+bytes([int(data,16)]) + bytes([xor])+ bytes([sum])
    # ser.write(comm)
    # sleep(0.2)
    return comm

def chkcard(uid,door_dev,sname,baurate,doortype,node):
    if doortype=='一般':   #設定一般門和鐵卷門開啟時間
        dooropentime=5
    else:
        dooropentime=2
    #relay.setup()
    #開啟資料庫連線
    # print('door_dev=',door_dev)
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c2=conn.cursor()
    c1=conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS cards(id TEXT,customer_id TEXT,card_uuid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_customers(id TEXT,booking_id TEXT,customer_id TEXT,source TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT,aircontrol TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS scanlog(cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT,auth TEXT,process TEXT,result TEXT)')    
    
    auth=""
    process=""
    result="0"

    today=str(datetime.now().strftime('%Y-%m-%d'))
    time=str(datetime.now().strftime('%H:%M:%S'))
    #10:15:08 (HH:MM:SS)
    if int(time[3:5])>=30:
        range_id=str(time[0:2])+':30'
        print('系統時段=',range_id)
    else:
        range_id=str(time[0:2])+':00'
        print('系統時段=',range_id)
    ser = serial.Serial(sname, baurate, timeout=1)
    c.execute('select * from cards where card_uuid=?' ,(uid,)) #找尋資料庫中, 是否有合法之卡號
    i=0
    for row in c: #資料庫筆數如果為0則表示無此卡號
        i+=1
    if i>=1:
        auth="合法卡"
        
        AR721R1ON=ar721comm(node,'0x21','0x82')   #door relay on
        AR721R1OFF=ar721comm(node,'0x21','0x83')  #door relay off
        AR721R2ON=ar721comm(node,'0x21','0x85')   #alarm relay on
        AR721R2OFF=ar721comm(node,'0x21','0x86')  #alarm relay off
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
                    result="1"
                    if door_dev=="AR721":
                        ser.write(AR721R1ON)
                        sleep(dooropentime)
                        ser.write(AR721R1OFF)
                    else:
                        relay.action(1,dooropentime,0)
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
                else:   #門狀態是開啟
                    if doortype=='鐵卷門':
                        process="全區卡-關門"
                        if door_dev=="AR721":
                            ser.write(AR721R2ON)
                            sleep(dooropentime)
                            ser.write(AR721R2OFF)
                        else:
                            relay.action(2,dooropentime,0)
                        relay.action(3,0,0)
                        relay.action(4,0,0)
                break
        if process=="":
            print('一般卡')
            process="非預約時段"
            if doortype=='一般':   #一般租借-一般門
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
                                result="1"
                                if door_dev=="AR721":
                                    ser.write(AR721R1ON)
                                    sleep(dooropentime)
                                    ser.write(AR721R1OFF)
                                else:
                                    relay.action(1,dooropentime,0)
                                if row[3]=='normal':
                                    relay.action(3,255,0)
                                    if row1[4] == '1':
                                        relay.action(4,255,0)
                                    else:
                                        relay.action(4,0,0)

            else:   #一般租借-鐵卷門
                if sensor0==1:  #S0=1 表示門狀態是關閉
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
                                    result="1"
                                    if door_dev=="AR721":
                                        ser.write(AR721R1ON)
                                        sleep(dooropentime)
                                        ser.write(AR721R1OFF)
                                    else:
                                        relay.action(1,dooropentime,0)
                                    
                                    if row[3]=='normal':
                                        relay.action(3,255,0)
                                        if row1[4] == '1':
                                            relay.action(4,255,0)
                                        else:
                                            relay.action(4,0,0)
                else:  #S0=0 表示門狀態是開啟
                    c.execute('select * from booking_customers where customer_id=?' ,(row[1],))
                    i=0
                    for row in c: #找尋booking_customers資料庫中, 是否有此客戶
                        i+=1
                        print('booking_id:第'+str(i)+'筆'+row[1])
                        if i>=1:
                            if door_dev=="AR721":
                                ser.write(AR721R2ON)
                                sleep(dooropentime)
                                ser.write(AR721R2OFF)
                            else:
                                relay.action(2,dooropentime,0)
                            relay.action(3,0,0)
                            relay.action(4,0,0)                            


    else:
        auth="非法卡"
        process="禁止進入"


    c.execute("INSERT INTO scanlog VALUES(?,?,?,0,?,?,?)", (uid,today,time,auth,process,result))
    conn.commit()
    conn.close()
    ser.close
    uploadlog()
if __name__=='__main__':
    uid='4077189990'
    #uid='1234567890'
    door_dev="AR721"
    chkcard(uid,door_dev,sname,baurate)