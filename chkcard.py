import sqlite3
from datetime import datetime, timedelta
import models.relay as relay
import WebApiClient.remote as remote
from time import sleep
import serial
from upload import uploadlog
import globals 




def initData():
    global _today
    global _range_id
    global _time
    _today=str(datetime.now().strftime('%Y-%m-%d'))
    _time=str(datetime.now().strftime('%H:%M:%S'))
    if int(_time[3:5])>=30:
        _range_id=str(_time[0:2])+':30'
    else:
        _range_id=str(_time[0:2])+':00'


def initGlobals():
    globals.initialize() 

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



def getCardByUid(uid):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from cards where card_uuid=?' ,(uid,)) #找尋資料庫中, 是否有合法之卡號
    card = c.fetchone()
    conn.close()
    return card
  
def getSpcardByCustomerId(customer_id):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from spcards where customer_id=?' ,(customer_id,))
    spcard = c.fetchone()
    conn.close()
    return spcard

def getNowBookingDataByCustomerId(customer_id):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
        'select bh.* '
        'from booking_customers as bc '
        'join booking_histories as bh '
        'on bc.booking_id = bh.id '
        'where bc.customer_id = ? and bh.date = ? and bh.range_id = ?',
        (
            customer_id,
            _today,
            _range_id,
        )
    )

    spcard = c.fetchone()
    conn.close()
    return spcard

def actionDoor(uid,userMode):
    sxstatus = relay.read_sensor()
    #S1=1 => 門狀態是關閉
    #S1=0 => 門狀態是開啟
    s1=sxstatus[0]
    # s1=1
    print('s1 status =',s1)
    if s1==1:
        # 開門
        openDoor()
        log(uid,'合法卡',userMode+'-開門',1)
    else:
        # 關門
        if globals._device.doortype=='鐵捲門':
            closeDoor()
            log(uid,'合法卡',userMode+'-關門',1)


def openDoor():
    print('openDoor')
    if globals._scanner.name=="AR721":
        AR721_R1_ON=ar721comm(1,'0x21','0x82')   #door relay on
        AR721_R1_OFF=ar721comm(1,'0x21','0x83')  #door relay off
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R1_ON)
        sleep(globals._device.opendoortime)
        ser.write(AR721_R1_OFF)
    else:
        relay.action(1,globals._device.opendoortime,0)
    


def closeDoor():
    print('closeDoor')
    if globals._scanner.name=="AR721":

        AR721_R2_ON=ar721comm(1,'0x21','0x85')   #alarm relay on
        AR721_R2_OFF=ar721comm(1,'0x21','0x86')  #alarm relay off
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R2_ON)
        sleep(globals._device.opendoortime)
        ser.write(AR721_R2_OFF)
    else:
        relay.action(2,globals._device.opendoortime,0)


def actionRelay(relayNo):
    sxstatus = relay.read_sensor()
    #S1=1 => 門狀態是關閉
    #S1=0 => 門狀態是開啟
    s1=sxstatus[0]
    # s1=1
    if s1==1:
        # 開門
        openRelay(relayNo)
    else:
        # 關門
        if globals._device.doortype=='鐵捲門':
            closeRelay(relayNo)

def openRelay(relayNo):
    print('openRelay : ',relayNo)
    relay.action(relayNo,255,0)

def closeRelay(relayNo):
    print('closeRelay : ',relayNo)
    relay.action(relayNo,0,0)
    

def log(uid,auth,process,result):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute("INSERT INTO scanlog VALUES(?,?,?,0,?,?,?)", (uid,_today,_time,auth,process,result))
    conn.commit()
    conn.close()
    uploadlog()

    



def chkcard(uid):
    print("____________chkcard_run__________________")
   

    # initData
    initData()
    # initGlobals()



    #取得Card資料
    card = getCardByUid(uid)
    if card == None:
        print('找不到Card資料 => 非法卡')
        log(uid,'非法卡','禁止進入',0)
        return 0


    
    #取得Spcard資料
    spcard = getSpcardByCustomerId(card[1])

    if spcard == None :
        print('找不到Spcard資料 => 找尋預約紀錄')
        #判斷預約紀錄
        nowBookingData = getNowBookingDataByCustomerId(card[1])
        if nowBookingData == None:
            print('找不到預約紀錄 => 不開門')
            log(uid,'合法卡','非預約時段',0)
            return 0
        actionDoor(uid,'租借時段')
        actionRelay(3)
        aircontrol = nowBookingData[4]
        if aircontrol == '1':
            actionRelay(4)
    else:
        actionDoor(uid,'全區卡')
        authority = spcard[2]
        if len(authority) > 0:
            authority_split = authority.split(',')
            for authority_relay in authority_split:
                actionRelay(int(authority_relay))
    
    


# if __name__=='__main__':
    # uid='4077189990'
    # uid='1479304897'
    # # uid='1111000125'
    # chkcard(uid)