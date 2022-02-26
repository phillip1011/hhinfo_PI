# from datetime import datetime
# import sqlite3

# #cardno  = uid
# cardno  = "1234567890"
# timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# text_file = open("/home/ubuntu/nfc/inputcardlog.txt", "a+")
# text_file.write(timenow+" "+str(cardno+'\n'))
# print(timenow +" Input CARD ="+str(cardno))
# text_file.close()

# conn=sqlite3.connect("db.sqlite")
# type(conn)
# cursor=conn.sursor()
# type(cursor)
# SQL='CREATE TABLE IF NOT EXISTS cardlog(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,card_nbr TEXT,yyyymmdd TEXT,hhmmss TEXT)'
# INSERT INTO cardlog(yyyymmdd,hhmmss,cardno) values(str(datetime.now().strftime('%Y-%m-%d')),str(datetime.now().strftime('%H:%M:%S')),cardno)

#---------------------------------------------------------------------
##RELAY板設定及讀取狀態
# import RPi.GPIO as GPIO
# GPIO.setwarnings(False) 	#disable warnings
# GPIO.setmode(GPIO.BCM)
# Relay_pin=[5,6,13,16,19,20,21,26]    #Relay BCM PIN:5,6,13,16,19,20,21,26
# sw = 1   #參數 OFF=1 , ON=0
# for i in range(8):
#     GPIO.setup(Relay_pin[i], GPIO.OUT) #設定為輸出模式
#     GPIO.output(Relay_pin[i], sw)
#     if (GPIO.input(Relay_pin[i]) == 1):
#         print("Relay "+ str(i) + "= 關閉" ) #讀取RELAY狀態
#     else:
#         print("Relay "+ str(i) + "= 開啟" ) #讀取RELAY狀態

#---------------------------------------------------------------------
# #Sensor板讀取狀態
# #Sensor BCM PIN = 17, 27, 22, 17, 27, 22
# import RPi.GPIO as GPIO
# GPIO.setwarnings(False) 	#disable warnings
# GPIO.setmode(GPIO.BCM)
# sensor_pin=[17, 27, 22, 12,23, 24, 25,18]
# for i in range(8):
#     #print(sensor_pin[i])
#     GPIO.setup(sensor_pin[i], GPIO.IN)
#     print(GPIO.input(sensor_pin[i]))  # 如果傳回0表示高電位HIGH
#---------------------------------------------------------------------
# 執行序 (當SENSOR 4觸發時, RELAY 1 開啟5秒
# import RPi.GPIO as GPIO
# import threading
# from time import sleep
# def sx_chk():
#     GPIO.setwarnings(False) 	#disable warnings
#     GPIO.setmode(GPIO.BCM)
#     sensor_pin=[17, 27, 22, 12,23, 24, 25,18]
#     RX_pin=[5,6,13,16,19,20,21,26]
#     GPIO.setup(sensor_pin, GPIO.IN)
#     GPIO.setup(RX_pin, GPIO.OUT)
#     sleep(1)
#     GPIO.output(RX_pin, 1) #初始值設定為OFF狀態
#     while True:     
#         for i in range(8):
#             sleep(0.1)
#             if GPIO.input(12)==0: #SENSOR4 作動時
#                 print("RELAY 1 要動作")
#                 GPIO.output(5, 0)
#                 sleep(5)
#                 GPIO.output(5, 1)
# if __name__=='__main__':
#     t1 = threading.Thread(target=sx_chk())
#     t1.setDaemon(True)
#     t1.start()
#---------------------------------------------------------------------
#找USB位置及設定硬體名稱
# import subprocess
# from time import sleep
# def get_process(cmd):
#     try:
#         item = subprocess.check_output(cmd, shell=True)
#         print(item)
#         sleep(100)
#         return item
#     except:
#         print("except")
#         return ''

# def get_serial_name(usb_names):
#     cmd = "sudo dmesg |grep 'converter now attached to ttyUSB' |grep"
#     for usb_name in usb_names:
#         cmd  = cmd + " '" + usb_name + "'"
#     print (cmd+"TEST1")
#     print (str(subprocess.check_output(cmd, shell=True))+"test2")
#     res = get_process(cmd)
#     items = str(res).split("\\n")
#     last_time = 0.0
#     serial_name ="ttyAMA0"
#     for item in items:
#         l1 = item.find('[')
#         l2 = item.find(']') 
#         if l1 > -1 and l2 > 0 :
#             time_sn = item[l1+1:l2-1]
#             this_time = float(time_sn)
#             if (this_time > last_time):
#                 last_time = this_time
#                 l3 = item.find('ttyUSB')
#                 if (l3 >0):
#                     serial_name = item[l3:l3+7]
#     return serial_name

# usb_names=["usb 1-1.1.3"]  #硬體名稱, 已固定下來
# sname = '/dev/' + get_serial_name(usb_names)
# print(sname)
# cmd = "sudo dmesg |grep 'converter now attached to ttyUSB' |grep"
# for usb_name in usb_names:
#     cmd  = cmd + " '" + usb_name + "'"
# print (cmd)
#---------------------------------------------------------------------
#執行序等待卡機讀取後寫入inputcardlog.txt
# import threading
# import serial
# import sqlite3
# from time import sleep
# from datetime import datetime

# def getdata():
#     com_error = 0
#     sname = '/dev/ttyUSB0'
#     ser = serial.Serial(sname, 9600, timeout=1)
#     if com_error == 1 :
#         print("quit")
#         return 
#     # 清空 READ BUFFER
#     output=''
#     try:   
#         output = ser.readline()
#     except:
#         ser.close()
#     if len(output) == 0: 
#         return ''

#     if  len(output) > 10  :        
#         print("字串長度=" + str(len(output)))
#         return output
#     else: 
#         output =''
#         return output
#     ser.close()

# def decode(datas):
#     i=0
#     for data1 in datas:     #例如字串: b'\x024077189990\r\n' 第1個字母直到2, 取10位
#         print(data1)
#         if (data1 == 2):
#             uid = (datas[i+1:i+11]).decode("utf-8") 
#             break
#         i =i +1
#     return str(uid)

# def get_event():    
#     output = getdata()
#     try:
#         uid = decode(output)
# #----------- modify by phillip 將刷卡卡號寫入  scanlog           inputcardlog.txt
#         # conn=sqlite3.connect("cardno.db")
#         # c=conn.cursor()
#         # c.execute('CREATE TABLE IF NOT EXISTS scanlog(cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT)')
#         # today=str(datetime.now().strftime('%Y%m%d'))
#         # time=str(datetime.now().strftime('%H%M%S'))
#         # c.execute("INSERT INTO scanlog VALUES("+ str(uid) + ","+ today+","+time+",0)")
#         # conn.commit()
#         # conn.close()
        
#         cardno = uid   #cardno  = "1234567890"
#         timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#         text_file = open("/home/ubuntu/nfc/inputcardlog.txt", "a+")
#         text_file.write(timenow+" "+str(cardno+'\n'))
#         print(timenow +" Input CARD ="+str(cardno))
#         text_file.close()
# #-----------
#         return uid
#     except:
#         return ''

# def do_read_r35c():
#     while True:
#         uid = get_event()
#         sleep(0.7)

# if __name__=='__main__':
#     t = threading.Thread(target=do_read_r35c())
#     t.setDaemon(True)
#     t.start()
# #---------------------------------------------------------------------
# import sqlite3
# cardno  = "1234567890"

# conn=sqlite3.connect("cardno.db")
# c=conn.cursor()
# conn=sqlite3.connect("cardno.db")
# c.execute('CREATE TABLE IF NOT EXISTS authcard(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,cardnbr TEXT,start_d TEXT,end_d TEXT,start_t TEXT,end_t TEXT)')

# c.execute("INSERT INTO cardlog VALUES(2,1234567890,1,1)")

# for row in c.execute('select * from cardlog'):
#     print(row)

# conn.commit()
# conn.close()
# #---------------------------------------------------------------------
# import os
# #import readlines
# def test():
#     #aa=os.system("ifconfig eth0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'")
#     aa=os.popen("ifconfig tun0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'")
#     #aa=os.popen("ifconfig eth0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'")
#     #type(aa)
#     bb=aa.readline()
#     if len(bb)>1:
#         print("己連線VPN")
#     else:
#         print("未連線VPN")


            # vpnchk=os.popen("ifconfig tun0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'")
            # vpnchk=vpnchk.readline()
            # if len(vpnchk)>1:
            #     print("己連線VPN")
            # else:
            #     print("未連線VPN,進行連線中")
            #     #PING WEB SRV
#----------------------------------------



    # bb=str(bb).split('\')
    # print(bb[0])
    # bb=str(bb).split('.')
    # print(bb)

    #print(len(bb))
    # if aa==0:
    #     print("BB")
    # else:
    #     print(aa)
    
# test()
    
    # try:   
    #     print("讀取readline:"+str(output))
    # except:
    #     print("例外關閉serial:"+str(ser))
    #     ser.close()

    
    #ser.close()  #如close會造成讀取不穩定
#aa=os.system("sudo /sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2")

#print(os.system("ifconfig tun0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'"))
#print(os.system("ifconfig eth0 |grep 'inet ' |cut -d ' ' -f2,10- | awk '{ print $1}'"))

#value=os.system("ifconfig eth0 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'  | cut -d' ' -f2")
#print(str(value)[0:15])
#print(aa)

 #---------------------------------------------------------------------
# import socket
# def getlocalip():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect((serverip, 80))
#     print(s.getsockname()[0])
#     ip = str(s.getsockname()[0])
#     s.close()
#     #return ip

# getlocalip()

# import time
# import requests
# import RPi.GPIO as GPIO
# headers = {'Content-Type': 'application/json'}
# #api_url_base = "http://" + serverip + ":" + str(port) +"/api/v1/remote/dcode"
# api_url_base="http://10.8.0.1:80/api/v1/remote/dcode"
# request_string = "token=aGhpbmZvOjIwMjAwMTE2MjIxMDM5&txcode=4077189990&controlip=10.8.1.151:4661&gateno=1&eventtime="+time.strftime("%Y%m%d%H%M%S", time.localtime())+"&r1status=0&r2status=0&r3status=1&r4status=1&s1status=0&s2status=0&s3status=0&s4status=0&s5status=0&s6status=0"
# print(api_url_base + "?" + request_string)
# response = requests.get(api_url_base, params=request_string, headers=headers, verify=False,timeout=5)

# print('this is response:'+ response.text)

# #from relay command()
# comstring='serverip=114.35.246.11&gateno=1&opentime=4'
# this_serverip = comstring[0:comstring.find("&")]
# comstring=comstring[comstring.find("&")+1:]  #去掉serverip=114.35.246.11&字
# #print(comstring)
# comms=comstring.split("&gate")
# #print(comms)


#----------------------------------------------------------
# import sqlite3
# from datetime import datetime
# import models.relay as relay


# def checkorder(uid):
#     #開啟資料庫連線
#     conn=sqlite3.connect("cardno.db")
#     c=conn.cursor()
#     #新增記錄

#     c.execute('CREATE TABLE IF NOT EXISTS cards(id TEXT,customer_id TEXT,card_uuid TEXT)')
#     c.execute('CREATE TABLE IF NOT EXISTS booking_customers(id TEXT,booking_id TEXT,customer_id TEXT)')
#     c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT)')
    
#     # id = '2'  #input cards table
#     # customer_id = '3'
#     # card_uuid = '3759416887'
#     # c.execute("INSERT INTO cards values (?,?,?)", (id,customer_id,card_uuid,))


#     # id = '8'    #input booking_customers table
#     # booking_id = '184633'
#     # customer_id = '2'
#     # c.execute("INSERT INTO booking_customers values (?,?,?)", (id,booking_id,customer_id,))


#     # id = '184633'    #input booking_customers table
#     # deviceid = '329'
#     # date = '20220111'
#     # range_id = '2000'
#     # c.execute("INSERT INTO booking_histories values (?,?,?,?)", (id,deviceid,date,range_id,))

#     #查詢記錄----------------------------------------------

#     today=str(datetime.now().strftime('%Y%m%d'))
#     time=str(datetime.now().strftime('%H%M%S'))

#     if int(time[2:4])>=30:
#         range_id=str(time[0:2])+'30'
#         print(range_id)
#     else:
#         range_id=str(time[0:2])+'00'
#         print(range_id)

#     c.execute('select * from cards where card_uuid=?' ,(uid,))
#     i=0
#     for row in c: #先掃看是否有筆數, 如果沒有直接跳出
#         i+=1
#     if i>=1:
#         print("合法卡號")
#         print('customers_id是'+row[1])
#         c.execute('select * from booking_customers where customer_id=?' ,(row[1],))
#         i=0
#         for row in c: #先掃看是否有筆數, 如果沒有直接跳出(會掃到多筆)
#             i+=1
#             print('booking_id:第'+str(i)+'筆'+row[1])
#             if i>=1:
#                 c1.execute('select * from booking_histories where id=? and date=? and range_id=?' ,(row[1],today,range_id))
#                 xx=0
#                 for row1 in c1: #先掃看是否有筆數, 如果沒有直接跳出(會掃到多筆)
#                     xx+=1
#                     if xx>=1:
#                         print(row1[0])    
#                         relay.action(1,5,0)
#             else:
#                 print("not in booking_customers")
#     else:
#         print("非法卡")

    
#     conn.commit()
#     conn.close()


# if __name__=='__main__':
#     uid='4077189990'
#     #uid='1234567890'
#     relay.setup()
#     checkorder(uid)

#-------------------------------------------------------------
# import RPi.GPIO as GPIO
# import models.relay as relay
# import time
# import WebApiClent.remote as remote
# GPIO.setwarnings(False)

# if __name__=='__main__':
#     clientip='192.168.16.183'
#     token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"

#     RX_pin=[5,6,13,16,19,20,21,26]
#     GPIO.setup(RX_pin, GPIO.OUT)

#     for i in range(8):
#         GPIO.setup(RX_pin[i], GPIO.OUT )
    
#     for i in range(8):
#         GPIO.output(RX_pin[i], 1)



#     #remote.monitor_sensor(clientip,token)
# import flask
# #import models.relay as relay
# from flask import jsonify, request
# import base64
# import json
# import time
# import threading
# import models.relay as relay
# import WebApiClent.update_time as update_time


# app = flask.Flask(__name__)
# app.config["DEBUG"] = False
# app.config['LIVESERVER_TIMEOUT'] = 2
# controlip="127.0.0.1"
# port = 80
# token_key=b'http://www.hhinfo.com.tw/'
# serverip="127.0.0.1"


# @app.route('/api/v2/remote/rcode', methods=['GET'])
# def apitest():
#     print("revice data")
#     return 0

# def checkserverip(request):
#     try:     
#         if request.form['serverip'] != serverip :
#             status_code = flask.Response(status=401)
#             return status_code
#     except:
#         status_code = flask.Response(status=401)
#         return status_code

# if __name__='__main__':
    
#     api.serverip  = checkip
#     api.controlip = controlip
#     api.port = 4661
#     api.token_key=token_key
    
#     test.run()

# from dataclasses import dataclass
# from time import sleep
# import serial
# import models

# def decode_ar721_event(data):
#     #if data[0] != 126:
#     #    return '', 0
#     #len1 = data[1];
#     #if (len(data) != len1 + 2):
#     #     return '', 1
#     #print (data[1])
#     if (data[1] == 4):
#         return '', 4
#     if (data[1] == 3 or data[1] == 11):
#         DateTimeString = "20" + str(data[9]) + "/" + str(data[8]) + "/" + str(data[7]) + " " + str(data[5]) + ":" + str(data[4]) + ":" + str(data[3])
#         print9=(DateTimeString)
#         UID =  bytearray(b'\x00\x00\x00\x00')
#         UID[0] = data[17]
#         UID[1] = data[18]
#         UID[2] = data[21]
#         UID[3] = data[22]
#         sn = int.from_bytes(UID, byteorder='big')
#         return DateTimeString,sn
#     else:
#         return '',0
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# #ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
# # ser.flushInput()  # flush input buffer
# # ser.flushOutput()  # flush output buffer
# #input=b'\x7E\x04\x01\x25\xdb\x01'  #get cardsnbr
# input=b'\x7E\x04\x01\x24\xDA\xFF'  #get time
# print('write str:',input)
# ser.write(input)
# ser.flush()
# sleep(0.2)
# output = ser.read()
# print('read str:',output)
# data=output

# print("年:"+str(data[11]))
# print("月:"+str(data[10]))
# print("日:"+str(data[9]))
# ser.close()
# #from dataclasses import dataclass
# from time import sleep
# import serial



# #ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# # if(ser.isOpen() == True):
# #     ser.close()

# #input=b'\x7e\x05\x01\x21\x82\x5d\x01'  #door relay on
# input=b'\x7e\x05\x01\x21\x83\x5c\x01'  #door relay off
# #input=b'\x7e\x05\x01\x21\x85\x5a\x01'  #alarm relay on
# #input=b'\x7e\x05\x01\x21\x86\x59\x01'  #alarm relay off
# #input=b'\x7e\x0e\x01\x83\x00\x01\x04\x41\xea\x4b\x04\xd2\x02\x01\x4d\x25'   #setting access PIN
# #while True:
# #input=b'\x7e\x04\x01\x25\xdb\x01'
# ser.write(input)
# sleep(0.2)
# ser.close
# output = ser.read(64)
# print(output)
# print(hex(output[0]))
# print(hex(output[1]))
# print(hex(output[2]))
# print(hex(output[3]))
# print(hex(output[4]))

import os
import json
import requests
import datetime
import WebApiClent.update_time as update_time
import sqlite3

serverip = "114.35.246.115"
port = 8080

def test():
    path = '/api/v1/data/time'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path
    
    
    # response = requests.get(api_url_base,'', headers=headers, verify=False,timeout=5)
   
    # print('伺服器回傳狀態:', response)
    # # Making a get request 
    response = requests.get(api_url_base) 
    
    # print response 
    print(response) 
    
    # print json content
    r = response.json()
    time = r['data']
    timeformat =  datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")

  
    update_time.time_tuple = (
        int(timeformat.strftime('%Y')),
        int(1),
        #int(timeformat.strftime('%m')),
        int(timeformat.strftime('%d')),
        int(timeformat.strftime('%H')),
        int(timeformat.strftime('%M')),
        int(timeformat.strftime('%S')),
        0, # Millisecond
    )
        #print (update_time.time_tuple)
    update_time.update()
    
    #print("自動校時成功",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #print("自動校時成功",datetime())
def test2():
    ip = '10.8.1.151:4661'   #controlip
    path = '/api/v1/data/device'
    request_string = "ip=" + str(ip)
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path
    response = requests.get(api_url_base,params=request_string, headers=headers) 
    
    # print response 
    print(response) 
    
    # print json content
    r = response.json()
    data = r['data']

    print(data['name']) 

def test3():
    ip = '10.8.1.151:4661'   #controlip
    path = '/api/v1/data/log'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path

   
    data = []
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    dev_c=conn.cursor()
    dev_c.execute('select * from scanlog limit 10')
    for row in dev_c:
        temp_obj = {
            "cardnbr": row[0],
            "date" : row[1],
            "time" : row[2],
            "auth" : row[3],
            "process" :row[4],
            "result" : row[5]
        }
        data.append(temp_obj)
        print(temp_obj)
     
    conn.commit()
    conn.close()

    # print(data)

    # print(data)
    postdata = {
        'ip' : ip,
        'data' :data
    }
    response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))
    print(response.json())
    print(response.status_code)

def test4():
    ip = '10.8.1.151:4661'   #controlip
    path = '/api/v1/data/log'
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) + path
   
    data = []
    cnt=0
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from scanlog where rtnflag=0')
    for row in c:
        temp_obj = {
            "cardnbr": row[0],
            "date" : row[1],
            "time" : row[2],
            "auth" : row[3],
            "process" :row[4],
            "result" : row[5]
        }
        data.append(temp_obj)
        cnt+=1
        # print(temp_obj)        
    postdata = {
        'ip' : ip,
        'data' :data
    }

    response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))
    #print(response.json())
    if cnt!=0:
        if response.status_code==200:
            print("上傳成功,共",cnt,"筆")
            c.execute('update scanlog set rtnflag=1 where rtnflag=0')
        else:
            print("上傳失敗")
    else:
        print("無上傳資料")
    conn.commit()
    conn.close()
test4()
