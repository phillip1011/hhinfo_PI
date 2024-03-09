import sqlite3
from time import sleep
from datetime import datetime, timedelta
import serial
import globals 
import threading
import sound as sound
import socket
buffer_minutes =''
delay_minutes =''
spcard_minutes =''

def initData():
    global _today
    global _range_id
    global _time
    global _buffer_range_id
    global _buffer_time
    global _delay_range_id
    global _delay_time

    _today=str(datetime.now().strftime('%Y-%m-%d'))
    _time=str(datetime.now().strftime('%H:%M:%S'))
    _range_id = criteriaRangeId(_time)

    buffer_minutes,=getBuffer_time()
    _buffer_time=str((datetime.now() + timedelta(minutes=int(buffer_minutes))).strftime('%H:%M:%S'))
    _buffer_range_id= criteriaRangeId(_buffer_time)
    
    delay_minutes,=getDelay_time()
    _delay_time=str((datetime.now() - timedelta(minutes=int(delay_minutes))).strftime('%H:%M:%S'))
    _delay_range_id= criteriaRangeId(_delay_time)

    #print("提早進入分鐘",buffer_minutes)
    #print("延後退場分鐘",delay_minutes)

    
def criteriaRangeId(time):
    if int(time[3:5])>=30:
        return str(time[0:2])+':30'
    else:
        return str(time[0:2])+':00'

def getSetting():
    return {
        "_today": _today,
        "_range_id" : _range_id,
        "_time" : _time,
        "_buffer_time" : _buffer_time,
        "_buffer_range_id" : _buffer_range_id,
        "_delay_time" : _delay_time,
        "_delay_range_id" : _delay_range_id,
    }



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

def getSpcard_time():
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select spcard_minutes from device') 
    spcard_time = c.fetchone()
    conn.close()
    return spcard_time

def getBuffer_time():
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select buffer_minutes from device') 
    buffer_time = c.fetchone()
    conn.close()
    return buffer_time

def getDelay_time():
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select delay_minutes from device') 
    delay_time = c.fetchone()
    conn.close()
    return delay_time

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
            _range_id
        )
    )
    nowBookingData = c.fetchone()
    conn.close()
    return nowBookingData

def getBufferBookingDataByCustomerId(customer_id):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
        'select bh.* '
        'from booking_customers as bc '
        'join booking_histories as bh '
        'on bc.booking_id = bh.id '
        'where bc.customer_id = ? and bh.date = ? and bh.range_id = ? ',
        (
            customer_id,
            _today,
            _buffer_range_id
        )
    )
    bufferBookingData = c.fetchone()
    conn.close()
    return bufferBookingData

def getDelayBookingDataByCustomerId(customer_id):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
        'select bh.* '
        'from booking_customers as bc '
        'join booking_histories as bh '
        'on bc.booking_id = bh.id '
        'where bc.customer_id = ? and bh.date = ? and bh.range_id = ? ',
        (
            customer_id,
            _today,
            _delay_range_id
        )
    )
    delayBookingData = c.fetchone()
    conn.close()
    return delayBookingData

def getOverTimeBookingDataByCustomerId(customer_id):
    print('_______',customer_id,_today,_range_id)
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
        'select bh.* '
        'from booking_customers as bc '
        'join booking_histories as bh '
        'on bc.booking_id = bh.id '
        'where bc.customer_id = ? and bh.date = ? and bh.range_id < ?',
        (
            customer_id,
            _today,
            _range_id,
        )
    )

    overTimeBookingData = c.fetchone()
    conn.close()
    return overTimeBookingData


def actionDoor(uid,userMode,relays):
    if globals._device.doortype != '鐵捲門' :
        openDoorWithRelays(relays,userMode)
        log(uid,'合法卡',userMode+'-開門',1)
    else : 
        sxstatus = globals._relay.readSensors()
        #S1=1 => 門狀態是關閉
        #S1=0 => 門狀態是開啟
        s1=sxstatus[0]
        print('s1 status =',s1)
        if s1==1:
            # 開門
            openDoorWithRelays(relays,userMode)
            log(uid,'合法卡',userMode+'-鐵卷門開門',1)
            return 1
        else:
            # 關門
            closeDoorWithRelays(relays,userMode)
            log(uid,'合法卡',userMode+'-鐵卷門關門',1)
            return 0


def ar721OpenDoor(node):
    try:
        AR721_R1_ON=ar721comm(node,'0x21','0x82')   #door relay on
        AR721_R1_OFF=ar721comm(node,'0x21','0x83')  #door relay off
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R1_ON)
        sleep(globals._device.opendoortime)
        ser.write(AR721_R1_OFF)
    except:
        print("ar721OpenDoor Error")

def ar721CloseDoor(node):
    try:
        AR721_R2_ON=ar721comm(node,'0x21','0x85')   #alarm relay on
        AR721_R2_OFF=ar721comm(node,'0x21','0x86')  #alarm relay off
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R2_ON)
        sleep(globals._device.opendoortime)
        ser.write(AR721_R2_OFF)
    except:
        print("ar721CloseDoor Error")

def ar837OpenDoor(node):
    try:
        AR721_R1_ON=ar721comm(node,'0x21','0x82')   #door relay on
        AR721_R1_OFF=ar721comm(node,'0x21','0x83')  #door relay off
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((globals._scanner.IP, globals._scanner.port))
        s.send(AR721_R1_ON)        
        sleep(globals._device.opendoortime)
        s.send(AR721_R1_OFF)
        s.close
    except:
        print("ar837OpenDoor Error")

def ar837CloseDoor(node):
    try:
        AR721_R2_ON=ar721comm(node,'0x21','0x85')   #alarm relay on
        AR721_R2_OFF=ar721comm(node,'0x21','0x86')  #alarm relay off
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((globals._scanner.IP, globals._scanner.port))
        s.send(AR721_R2_ON)        
        sleep(globals._device.opendoortime)
        s.send(AR721_R2_OFF)
        s.close
    except:
        print("ar721CloseDoor Error")

def openDoorWithRelays(relays,userMode):
    print('openDoor')
    #openDoorSound(userMode)
    globals._relay.action(1,globals._device.opendoortime,0)
    if globals._scanner.scannerName=="AR721":
        nodesCount = globals._scanner.nodesCount
        for x in range(nodesCount):
            node = x+1
            t6 = threading.Thread(target=ar721OpenDoor, args=(node,))
            t6.setDaemon(True)
            t6.start()
            sleep(1)
    elif globals._scanner.scannerName=="AR837":
        nodesCount = globals._scanner.nodesCount
        for x in range(nodesCount):
            node = x+1
            t6 = threading.Thread(target=ar837OpenDoor, args=(node,))
            t6.setDaemon(True)
            t6.start()
            sleep(1)

    openDoorSound(userMode)
    for relay in relays:
        openRelay(int(relay))
    

def closeDoorWithRelays(relays,userMode):
    print('closeDoor')
    globals._relay.action(2,globals._device.opendoortime,0)
    if globals._scanner.scannerName=="AR721":
        nodesCount = globals._scanner.nodesCount
        for x in range(nodesCount):
            node = x+1
            t7 = threading.Thread(target=ar721CloseDoor, args=(node,))
            t7.setDaemon(True)
            t7.start()
            sleep(1)
    closeDoorSound(userMode)
    # for relay in relays:
    #     closeRelay(int(relay))

def openDoorSound(userMode):
    if userMode=='全區卡':
        sound.spcardOpenDoorSound()
    else:
        sound.openDoorSound()
        
def closeDoorSound(userMode):
    if userMode=='全區卡':
        sound.spcardCloseDoorSound()
    else:
        sound.closeDoorSound()

def openRelay(relayNo):
    print('openRelay : ',relayNo)
    globals._relay.action(relayNo,255,0)
    #112/9/11 mark 因影響開門時間
    #if relayNo==3:
    #    sound.openR3Sound()
    #elif relayNo==4:
    #    sound.openR4Sound()
def closeRelay(relayNo):
    print('closeRelay : ',relayNo)
    globals._relay.action(relayNo,0,0)
    if relayNo==3:
        sound.closeR3Sound()
    elif relayNo==4:
        sound.closeR4Sound()
def log(uid,auth,process,result):
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute("INSERT INTO scanlog VALUES(?,?,?,0,?,?,?)", (uid,_today,_time,auth,process,result))
    conn.commit()
    conn.close()


def chkcard(uid):
    print("____________chkcard_run__________________")
    initData()
    #取得Card資料
    card = getCardByUid(uid)
    if card == None:
        print('找不到Card資料 => 非法卡')
        log(uid,'非法卡','禁止進入',0)
        sound.nonRegisterCard()
        return 0
    
    #取得Spcard資料
    spcard = getSpcardByCustomerId(card[1])

    if spcard == None :
        print('找不到Spcard資料 => 找尋預約紀錄')
        #判斷預約紀錄
        nowBookingData = getNowBookingDataByCustomerId(card[1])
        if nowBookingData == None:
            if buffer_minutes !=0:
                print("找尋緩衝提前時段")
                bufferBookingData = getBufferBookingDataByCustomerId(card[1])
                if bufferBookingData !=None:
                    authority_relay = [3]
                    print("緩衝提前時段,開啟R3")
                    actionDoorReturn = actionDoor(uid,'緩衝提前時段',authority_relay)
                    return 0

            if delay_minutes !=0:
                print("找尋緩衝延後時段")
                delayBookingData = getDelayBookingDataByCustomerId(card[1])
                if delayBookingData !=None:
                    authority_relay = [3]
                    print("緩衝延後時段,開啟R3")
                    actionDoorReturn = actionDoor(uid,'緩衝延後時段',authority_relay)
                    return 0
            
            if globals._device.doortype=='鐵捲門' :
                print('找不到預約紀錄 => 不開門 , 找尋超時紀錄')
                overTimeBookingData = getOverTimeBookingDataByCustomerId(card[1])
                if overTimeBookingData == None :
                    print('找不到超時預約紀錄 => 不關門')
                    log(uid,'合法卡','非預約時段',0)
                    sound.nonAuthCard()
                else:
                    sxstatus = globals._relay.readSensors()
                    #S1=1 => 門狀態是關閉
                    #S1=0 => 門狀態是開啟
                    s1=sxstatus[0]
                    if s1==0:
                        print('找到超時預約紀錄 => 關門')
                        closeDoorWithRelays([3,4],'一般卡')
                        log(uid,'合法卡','超時關門',1)
                    else:
                        sound.nonAuthCard()    
                return 0
            else:
                log(uid,'合法卡','非預約時段',0)
                sound.nonAuthCard()
                return 0
        else:
            #print('my _device id is:', globals._device.dev_id)
            #print('bh.device id is:',nowBookingData[1])
            authority_relay=[]
            if globals._device.dev_id==nowBookingData[1] :#判斷是否為本機預約資料,用於公用門
                authority_relay = [3]
                aircontrol = nowBookingData[4]
                if aircontrol == '1':
                    authority_relay.append(4)
            actionDoorReturn = actionDoor(uid,'租借時段',authority_relay)
     
            
          
    else:
        print("全區卡")
        spcard_minutes,=getSpcard_time()
        T1=datetime.now()
        T2=T1 + timedelta(minutes=int(spcard_minutes))
        conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        c=conn.cursor()
        c.execute('DELETE FROM spcard_time')
        c.execute("INSERT INTO spcard_time values (?,?,?,?)", (
            uid,
            T1,
            T2,
            spcard[2]
            )
        )
        conn.commit()
        conn.close()


        authority = spcard[2]
        if authority == '':
            authority_split=[]
        else:
            authority_split = authority.split(',')
        #print('authority_split : ',authority_split)
        actionDoorReturn = actionDoor(uid,'全區卡',authority_split)



#if __name__=='__main__':


    #uid='4077189990'
    # uid='1479304897'
    # uid='1111000125'
    #chkcard(uid)

