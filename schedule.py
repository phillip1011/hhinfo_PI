import sqlite3
from datetime import datetime
import globals
import configparser
import chkcard

rxstatus = [0, 0, 0, 0]
sxstatus = [0, 0, 0, 0, 0, 0]
controlip=""
poweredByTime=""
spcard_auth_ac="No"


def chk_sp_auth():
    #print("檢查是否有全區卡佔用")
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
    'select * from spcard_time where end_time>?', 
    (datetime.now(),)
    )
    spcard_auth = c.fetchone()
    conn.close()

    if spcard_auth != None:
        #print("全區卡時段佔用中")
        return 1
    else:
        #print("無全區卡佔用中")
        return 0

def spcard_Ry(relays,spcard_auth_ac):
    relays=relays.split(',')
    for relay in relays:
        if relay=="4":
            spcard_auth_ac="YES"
    if spcard_auth_ac=="No":
        globals._relay.action(4,0,0)


def initGlobals():
    #globals.ServerModel()
    globals.initRelay()
    globals.initDevice()
    globals._relay.setupGPIO()
    #globals.initScanner()    #不能和ar721.do_read_ar721同時跑, ser會誤判

def chkRyStatus():
    if globals._device.mode =='手動':
        print('手動模式, 不關閉Relay')
        return 0
    if globals._device.style =='公用' and globals._device.is_booking =='0':
        print('不可預約公用門, 不檢查Relay')
        return 0

    #先計算bufftime and delaytime
    chkcard.initData()
    timerange = chkcard.getSetting()
    #print("_range_id:",timerange['_range_id'])
    #print("_buffer_time:",timerange['_buffer_time'])
    #print("_buffer_range_id:",timerange['_buffer_range_id'])
    #print("_delay_time:",timerange['_delay_time'])
    #print("_delay_range_id:",timerange['_delay_range_id'])

    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute(
        'select * '
        'from booking_histories '
        'where date=? and deviceid=? and range_id = ? '
        'order by aircontrol desc' ,
        (
            timerange['_today'],
            globals._device.dev_id,
            timerange['_range_id']
        )
    )
 
    data = c.fetchone()
    if data == None:
        print("本時段無預約,檢查是否有延後關燈時間")
        conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
        c=conn.cursor()
        c.execute(
            'select * '
            'from booking_histories '
            'where date=? and deviceid=? and range_id = ? '
            'order by aircontrol desc' ,
            (
                timerange['_today'],
                globals._device.dev_id,
                timerange['_delay_range_id']
            )
        )
        data = c.fetchone()
        conn.close()

        if data != None:
            #延後退場時段
            if chk_sp_auth()==1:
                print("延後退場時段內, 全區卡佔用中")

                #if spcard_auth != None:
                #    spcard_Ry(spcard_auth[3],spcard_auth_ac)
            else:
                print("延後退場時段,無全區卡佔用中,本時段無預約:延時中,先關閉R4")
                globals._relay.action(4,0,0)
        else:
            #非延後退場時段
            if chk_sp_auth()==1:
                print("非延後退場時段,全區卡佔用中")
                #if spcard_auth != None:
                #    spcard_Ry(spcard_auth[3],spcard_auth_ac)
            else:
                #檢查是否在提早使用時段內, 如果是則不做改變
                conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
                c=conn.cursor()
                c.execute(
                    'select * '
                    'from booking_histories '
                    'where date=? and deviceid=? and range_id = ? '
                    'order by aircontrol desc' ,
                    (
                        timerange['_today'],
                        globals._device.dev_id,
                        timerange['_buffer_range_id']
                    )
                )
                data = c.fetchone()
                conn.close()
                if data != None:
                    print("提前時段,無全區卡佔用中,本時段無預約:保持原狀態")
                    return 0
                else:
                    print("非延後退場時段,無全區卡佔用中,本時段無預約:關閉R3及R4")
                    globals._relay.action(3,0,0)
                    globals._relay.action(4,0,0)
        return 0
    
    else:
        #有預約記錄
        if poweredByTime == "true":   #時間到才送電, 如果是刷卡送電模式, 電燈是刷卡時再送電
            print("本時段有預約:開啟R3並檢查是否開啟R4")
            globals._relay.action(3,255,0)
            if data[4] == '1':
                print("有預約冷氣:開啟R4")
                globals._relay.action(4,255,0)
        if chk_sp_auth()==0:
            print ("無全區卡佔用")
            if data[4] == '0':  #不管是時間送電還是刷卡送電,只要沒預約都斷冷氣電源
                globals._relay.action(4,0,0)  

    conn.commit()
    conn.close()


if __name__=='__main__':
    cf = configparser.ConfigParser()
    cf.read("/home/ubuntu/hhinfo_PI/config.ini")
    poweredByTime = cf.get("ServerConfig", "poweredByTime")

    initGlobals()
    chkRyStatus() 