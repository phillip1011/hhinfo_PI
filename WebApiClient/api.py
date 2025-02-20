import flask
import sqlite3
from flask import jsonify, request
import base64
import json
import time
import sqlite3
import threading
import WebApiClient.update_time as update_time
import models.ar721 as ar721
import models.AR837TCP as ar837
import socket
from chkcard import ar721comm, getSpcard_time
from datetime import datetime, timedelta
from time import sleep
import serial
import struct
import globals
import sound as sound
conn = sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
cur = conn.cursor()
cur.execute('select * from node')
nodedata = cur.fetchall()
conn.close()    

print("____________api.py run______________________")
app = flask.Flask(__name__)
app.config["DEBUG"] = False
app.config['LIVESERVER_TIMEOUT'] = 2









@app.route('/api/v2/remote/rcode', methods=['GET'])
def apitest():
    print("revice data")
    return 0




def white_spcardtime(spcard_auth):
    spcard_minutes,=getSpcard_time()
    T1=datetime.now()
    T2=T1 + timedelta(minutes=int(spcard_minutes))
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    if spcard_auth=='3,4':
        c.execute('DELETE FROM spcard_time')
    else:
        c.execute('DELETE FROM spcard_time where end_time<?',(datetime.now(),))

    c.execute("INSERT INTO spcard_time values (?,?,?,?)", (
        '遠端操作',
        T1,
        T2,
        spcard_auth
        )
    )
    conn.commit()
    conn.close()

def verifyToken(receiveToken):
    allowToken = globals._server.token
    if receiveToken != allowToken:
        print('receiveToken :' + receiveToken + ' != allowToken : '+allowToken)
        return False
    return True

def verifyServerIp(reviceServerIp):
    allowServerIp = globals._server.serverip
    if globals._server.verifyserverip == 'false' :
        return True

    if reviceServerIp != allowServerIp:
        print('verifyServerIp - receiveIP : '+str(reviceServerIp) +' != allowIP : '+str(allowServerIp))
        return False
    return True


def ar721OpenDoor(node,opentime,waittime):
    AR721_R1_ON=ar721comm(node,'0x21','0x82')   #door relay on
    AR721_R1_OFF=ar721comm(node,'0x21','0x83')  #door relay off
    if waittime!=0:
        time.sleep(waittime)
    try:
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R1_ON)
        sleep(opentime)
        ser.write(AR721_R1_OFF)
        sleep(1)
        ser.write(AR721_R1_OFF)
        print("remote ar721OpenDoor node:",node," success")
    except:
        print("remote ar721OpenDoor node:",node," Error")

def ar721CloseDoor(node,opentime,waittime):
    AR721_R2_ON=ar721comm(node,'0x21','0x85')   #alarm relay on
    AR721_R2_OFF=ar721comm(node,'0x21','0x86')  #alarm relay off
    if waittime!=0:
        time.sleep(waittime)
    try:
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R2_ON)
        sleep(opentime)
        ser.write(AR721_R2_OFF)
        sleep(1)
        ser.write(AR721_R2_OFF)       
        print("remote ar721CloseDoor node:",node,"success")

    except:
        print("remote ar721CloseDoor node:",node," Error")

def ar721action(gateno,dooropentime,waittime):
    nodesCount = globals._scanner.nodesCount
    for x in range(nodesCount):
        node = x+1
        if(gateno ==1):
            t = threading.Thread(target=ar721OpenDoor, args=(node, dooropentime, waittime))
        else:
            t = threading.Thread(target=ar721CloseDoor, args=(node, dooropentime, waittime))
        t.setDaemon(True)
        t.start()
        sleep(1)

def ar837action(gateno,dooropentime,waittime):  
    
    condition = True
    datano = 0
    while condition == True:        
        try:
            host = nodedata[datano][7]
            port = int(nodedata[datano][8])
            hostname = nodedata[datano][4]
            node = int(nodedata[datano][2])
            datano = datano + 1
            if(gateno ==1):
                t = threading.Thread(target=ar837OpenDoor, args=(node, host, port,hostname, dooropentime, waittime))
            else:
                t = threading.Thread(target=ar837CloseDoor, args=(node, host, port,hostname, dooropentime, waittime))
            t.setDaemon(True)
            t.start()
            sleep(1)
        except:
            condition = False

def ar837OpenDoor(node, host, port,hostname, opentime, waittime):

    AR721_R1_ON=ar721comm(node,'0x21','0x82')   #door relay on
    AR721_R1_OFF=ar721comm(node,'0x21','0x83')  #door relay off
    
    if waittime!=0:
        time.sleep(waittime)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(AR721_R1_ON)        
        sleep(opentime)
        s.send(AR721_R1_OFF)        
        sleep(1)
        s.send(AR721_R1_OFF)
        s.close
        print("AR837:",hostname,"OpenDoor success")
    except:
        print("AR837:",hostname,"OpenDoor Error")

def ar837CloseDoor(node, host, port,hostname, opentime, waittime):
    AR721_R2_ON=ar721comm(node,'0x21','0x85')   #alarm relay on
    AR721_R2_OFF=ar721comm(node,'0x21','0x86')  #alarm relay off
    if waittime!=0:
        time.sleep(waittime)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(AR721_R2_ON)        
        sleep(opentime)
        s.send(AR721_R2_OFF)
        sleep(1)
        s.send(AR721_R2_OFF)
        s.close
        print("AR837:",hostname,"CloseDoor success")
    except:
        print("AR837:",hostname,"CloseDoor Error")



@app.route('/api/v3/remote/control', methods=['POST'])
def api01():
    
    try:
        token = request.headers.get('token')

    except:
        status_code = flask.Response(status=401)
        return status_code

    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
        
    try:
        revice_data = json.loads(request.data)
        if  verifyServerIp(revice_data["serverip"]) != True:
            status_code = flask.Response(status=403)
            return status_code
        for value in revice_data["relay"]:
            gateno = revice_data["relay"][value]["gateno"]
            print("開啟腳位",gateno)
            opentime = revice_data["relay"][value]["opentime"]
            waittime = revice_data["relay"][value]["waittime"] 
            if isinstance(gateno,int) and isinstance(opentime,int) and isinstance(waittime,int):
                globals._relay.action(gateno,opentime,waittime)
                if (gateno == 1 or gateno ==2) and globals._scanner.scannerName[0:5] == "AR721":
                    ar721action(gateno,opentime,waittime)
                elif(gateno == 1 or gateno ==2) and globals._scanner.scannerName[0:5] == "AR837":
                    ar837action(gateno,opentime,waittime)
                   
        sleep(0.1)
        rt = {
            "controlip": globals._device.localip,
            "relay": globals._relay.readRelays(),
            "sensor": globals._relay.readSensors()
        }
        response = app.response_class(
            response=json.dumps(rt),
            status= 203,
            mimetype='application/json'
        )
        if gateno==1:
            ts1 = threading.Thread(target=sound.remoteOpenDoorSound)
            ts1.setDaemon(True)
            ts1.start()
        elif gateno==2:
            ts2 = threading.Thread(target=sound.remoteCloseDoorSound)
            ts2.setDaemon(True)
            ts2.start()
        elif gateno==3:
            if opentime==255:
                ts3 = threading.Thread(target=sound.remoteOpenR3Sound)
                ts3.setDaemon(True)
                ts3.start()
                white_spcardtime('3')
            elif opentime==0:
                ts4 = threading.Thread(target=sound.remoteCloseR3Sound)
                ts4.setDaemon(True)
                ts4.start()
        elif gateno==4:
            if opentime==255:
                ts5 = threading.Thread(target=sound.remoteOpenR4Sound)
                ts5.setDaemon(True)
                ts5.start()
                white_spcardtime('3,4')
            elif opentime==0:
                ts6 = threading.Thread(target=sound.remoteCloseR4Sound)
                ts6.setDaemon(True)
                ts6.start()
        return response

    except:
        status_code = flask.Response(status=502)
        return status_code


@app.route('/api/v3/remote/control/relay/<int:id>', methods=['GET'])
def api01A(id):
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
        
    if request.method == "GET":      
        rc2 = {"controlip": globals._device.localip}
        relay_status = {}
        temp = {str(id) : str(globals._relay.readRelays()[id])}
        relay_status.update(temp)
        rc2.update({"relay": relay_status})
        response = app.response_class(
            response=json.dumps(rc2),
            status=200,
            mimetype='application/json'
        )
        return response

@app.route('/api/v3/remote/control/sensor/<int:id>', methods=['GET'])
def api01B(id):
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
        
    if request.method == "GET":       
        rc2 = {"controlip": globals._device.localip}
        sensor = globals._relay.readSensors()
        sensor_status = {}
        temp = {str(id) : str(sensor[id])}
        sensor_status.update(temp)
        rc2.update({"sensor": sensor_status})
        response = app.response_class(
            response=json.dumps(rc2),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route('/api/v3/remote/control/time', methods=['POST'])
def api02():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code

    if request.method == 'POST':       
        try:
            test = json.loads(request.data)
        except:
            status_code = flask.Response(status=502)
            return status_code

        revice_data = json.loads(request.data)
        print('control/time receive')
        print(revice_data)
        if  verifyServerIp(revice_data["serverip"]) != True:
            status_code = flask.Response(status=403)
            return status_code

        #print(type(revice_data), revice_data)
        update_time.time_tuple = (
            int(revice_data["Year"]),   # Year
            int(revice_data["Month"]),  # Month
            int(revice_data["Day"]),  # Day
            int(revice_data["Hour"]),  # Hour
            int(revice_data["Minute"]),  # Minute
            int(revice_data["Second"]),  # Second
             0, # Millisecond
        )
        #print (update_time.time_tuple)
        update_time.update()
        #update_time.update2(revice_data)
        status_code = flask.Response(status=203)
        if globals._scanner.scannerName=="AR837":
            condition = True
            nodecounting = 0
            while condition == True:
                x = nodecounting
                nodecounting = nodecounting + 1
                try:
                    if int(nodedata[x][14])==1:
                        host = nodedata[x][7]
                        port = int(nodedata[x][8])
                        hostname = nodedata[x][4]
                        node = int(nodedata[x][2])
                        
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((host,port))
                        sysyy=int(datetime.now().strftime('%y'))
                        sysmm=int(datetime.now().strftime('%m'))
                        sysdd=int(datetime.now().strftime('%d'))
                        syshh=int(datetime.now().strftime('%H'))
                        sysmin=int(datetime.now().strftime('%M'))
                        sysss=int(datetime.now().strftime('%S'))
                        sysww=int(datetime.now().strftime('%w'))
                        if sysww==0:
                            sysww=7
                        #print("PI系統時間=",sysyy,'-',sysmm,'-',sysdd,' ',syshh,':',sysmin,':',sysss)
                        xor=255^node^35^sysss^sysmin^syshh^sysww^sysdd^sysmm^sysyy                    
                        sum=(node+35+sysss+sysmin+syshh+sysww+sysdd+sysmm+sysyy+xor)
                        sum =sum % 256
                        input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
                        s.send(input)
                        sleep(0.2)
                        print(hostname,"IP:",host,"node=",node, "校時完成")     
                
                except:
                    print(hostname,"IP:",host,"node=",node, "校時失敗")
                condition = False
        
                    
        if globals._scanner.scannerName=="AR721":
            nodesCount = globals._scanner.nodesCount
            for x in range(nodesCount):
                node = x+1
                try:
                    ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
                    sysyy=int(datetime.now().strftime('%y'))
                    sysmm=int(datetime.now().strftime('%m'))
                    sysdd=int(datetime.now().strftime('%d'))
                    syshh=int(datetime.now().strftime('%H'))
                    sysmin=int(datetime.now().strftime('%M'))
                    sysss=int(datetime.now().strftime('%S'))
                    sysww=int(datetime.now().strftime('%w'))
                    if sysww==0:
                        sysww=7
                    print("PI系統時間=",sysyy,'-',sysmm,'-',sysdd,' ',syshh,':',sysmin,':',sysss)
                    xor=255^node^35^sysss^sysmin^syshh^sysww^sysdd^sysmm^sysyy
                    
                    sum=(node+35+sysss+sysmin+syshh+sysww+sysdd+sysmm+sysyy+xor)
                    sum =sum % 256
                    input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
                    # print(input)
                    ser.write(input)
                except:
                    print("ar721 update time Error")
                sleep(0.2)
                print(globals._scanner.scannerName,"node=",node, "校時完成")
        print (status_code)
        return status_code

   
    



@app.route('/api/v3/remote/syns/cards', methods=['POST'])
def apicards():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
   
    revice_data = json.loads(request.data)
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c.execute('DROP TABLE cards')
    c.execute('CREATE TABLE IF NOT EXISTS cards(id TEXT,customer_id TEXT,card_uuid TEXT)')
    c.execute('DELETE FROM cards')
    for value in revice_data:
        c.execute("INSERT INTO cards values (?,?,?)", (value["id"],value["customer_id"],value["card_uuid"],))
    conn.commit()
    conn.close()
    status_code = flask.Response(status=203)
    return status_code


@app.route('/api/v3/remote/syns/booking_customers', methods=['POST'])
def apibooking_customers():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
  
    revice_data = json.loads(request.data)
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS booking_customers(id TEXT,booking_id TEXT,customer_id TEXT,source TEXT)')
    c.execute('DELETE FROM booking_customers')
    for value in revice_data:
        c.execute("INSERT INTO booking_customers values (?,?,?,?)", (value["id"],value["booking_id"],value["customer_id"],value["source"],))
    conn.commit()
    conn.close()
    status_code = flask.Response(status=203)
    return status_code
   

@app.route('/api/v3/remote/syns/booking_histories', methods=['POST'])
def apibooking_histories():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
 
    revice_data = json.loads(request.data)
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS booking_histories(id TEXT,deviceid TEXT,date TEXT,range_id TEXT,aircontrol TEXT)')
    c.execute('DELETE FROM booking_histories')
    for value in revice_data:
        c.execute("INSERT INTO booking_histories values (?,?,?,?,?)", (value["id"],value["deviceid"],value["date"],value["range_id"],value["aircontrol"],))
    conn.commit()
    conn.close()
    status_code = flask.Response(status=203)
    return status_code
    

@app.route('/api/v3/remote/syns/spcards', methods=['POST'])
def apispcards():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
    
    revice_data = json.loads(request.data)
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS spcards(id TEXT,customer_id TEXT,authority TEXT)')
    c.execute('DELETE FROM spcards')
    for value in revice_data:
        c.execute("INSERT INTO spcards values (?,?,?)", (value["id"],value["customer_id"],value["authority"],))
    conn.commit()
    conn.close()
    status_code = flask.Response(status=203)
    return status_code

@app.route('/api/v3/remote/syns/device', methods=['POST'])
def apiDeviceDate():
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
  
    revice_data = json.loads(request.data)
    conn=sqlite3.connect("cardno.db")
    c=conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS device('
        'id TEXT,'
        'ip TEXT,'
        'mac TEXT,'
        'local_ip TEXT,'
        'ip_mode TEXT,'
        'family TEXT,'
        'name TEXT,'
        'description TEXT,'
        'group_id TEXT,'
        'mode TEXT,'   
        'style TEXT,'
        'type TEXT,'
        'is_booking TEXT,'
        'status TEXT,'
        'kernel TEXT,'
        'buffer_minutes INTEGER ,'
        'delay_minutes INTEGER,'
        'spcard_minutes INTEGER,'
        'node_protocol TEXT,'
        'powered_by_time TEXT)'
    )
    c.execute('DELETE FROM device')
    value = revice_data
    c.execute('INSERT INTO device values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
        value["id"],
        value["ip"],
        value["mac"],
        value["local_ip"],
        value["ip_mode"],
        value["family"],
        value["name"],
        value["description"],
        value["group_id"],
        value["mode"],
        value["style"],
        value["type"],
        value["is_booking"],
        value["status"],
        value["kernel"],
        value["time_buffer_start"],
        value["time_buffer_end"],
        value["spcard_time"],  
        value["node_protocol"],  
        value["powered_by_time"]   
        )
    )
    conn.commit()
    conn.close()
    status_code = flask.Response(status=203)

    globals.initDevice() 

    return status_code
  

@app.route('/api/v3/remote/syns/openword', methods=['POST'])
def apiopenword():
    #開門密碼
    token = request.headers.get('token')
    if verifyToken(token) != True:
        status_code = flask.Response(status=401)
        return status_code
    
    revice_data = json.loads(request.data)
    #要加型態判斷

    node=revice_data['node']
    func='0x83'
    addr='00001'
    site='01089'
    card='59979'
    PIN=revice_data['pwd']
    
    addrH=struct.pack(">H",int(addr))
    addrH=addrH[0]
    addrL=struct.pack(">H",int(addr))
    addrL=addrL[1]
    siteH=struct.pack(">H",int(site))
    siteH=siteH[0]
    siteL=struct.pack(">H",int(site))
    siteL=siteL[1]
    cardH=struct.pack(">H",int(card))
    cardH=cardH[0]
    cardL=struct.pack(">H",int(card))
    cardL=cardL[1]
    pinH=struct.pack(">H",int(PIN))
    pinH=pinH[0]
    pinL=struct.pack(">H",int(PIN))
    pinL=pinL[1]

    #xor=0xff^node^int(func,16)^0x00^0x1^0x4^0x41^0xea^0x4b^0x4^0xd2^0x2^0x1
    xor=0xff ^ int(node,16) ^ int(func,16) ^ addrH ^ addrL ^ siteH ^ siteL ^ cardH ^ cardL ^ pinH ^ pinL ^ 0x2 ^ 0x1
    sum=int(node,16) + int(func,16) + addrH + addrL + siteH + siteL + cardH + cardL + pinH + pinL + 0x2 + 0x1 + xor
    sum =sum % 256
    # print('xor=',hex(xor))
    # print('sum=',hex(sum))
    comm=(
        b'\x7e\x0e'+ 
        bytes([int(node,16)])+ 
        bytes([int(func,16)])+ 
        bytes([addrH])+
        bytes([addrL])+
        bytes([siteH])+
        bytes([siteL])+
        bytes([cardH])+
        bytes([cardL])+
        bytes([pinH])+
        bytes([pinL])+
        b'\x02\x01' + 
        bytes([xor])+ 
        bytes([sum])
    )
    ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
    ser.write(comm)
    sleep(0.2)

    status_code = flask.Response(status=203)
    return status_code
def run():
    print("____API run_____port : "+str(globals._device.localport))
    app.run(debug=False, use_reloader=False, threaded=False, host="0.0.0.0", port=globals._device.localport)
