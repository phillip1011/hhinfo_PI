import flask
#import models.relay as relay
from flask import jsonify, request
import base64
import json
import time
import sqlite3
import threading
import models.relay as relay
import WebApiClent.update_time as update_time
import models.ar721 as ar721
from chkcard import ar721comm
from datetime import datetime
from time import sleep
import serial
import struct

app = flask.Flask(__name__)
app.config["DEBUG"] = False
app.config['LIVESERVER_TIMEOUT'] = 2
#controlip="127.0.0.1"
port = 80
#token_key=b'http://www.hhinfo.com.tw/'
#serverip="127.0.0.1"


@app.route('/api/v2/remote/rcode', methods=['GET'])
def apitest():
    print("revice data")
    return 0

def checkserverip(request):
    try:     
        if request.form['serverip'] != serverip :
            status_code = flask.Response(status=401)
            return status_code
    except:
        status_code = flask.Response(status=401)
        return status_code




def ar721action(dooropentime):
    ser = serial.Serial(sname, baurate, timeout=1)
    AR721R1ON=ar721comm(1,'0x21','0x82')   #door relay on
    AR721R1OFF=ar721comm(1,'0x21','0x83')  #door relay off                    
    ser.write(AR721R1ON)
    time.sleep(dooropentime)
    ser.write(AR721R1OFF)

@app.route('/api/v3/remote/control', methods=['POST','GET'])
def api01():
    try:
        test = request.headers.get('token')

    except:
        status_code = flask.Response(status=401)
        return status_code

    token_base64 = request.headers.get('token')
    # print(token_base64)
    token = base64.b64decode(str(token_base64)+"=")
    urlstring = request.url
    # print(token)
    # print (request.method)
    if token != token_key:
        status_code = flask.Response(status=401)
        return status_code
        
    if request.method == 'POST':
        try:
            test = json.loads(request.data)
        except:
            status_code = flask.Response(status=502)
            return status_code

        revice_data = json.loads(request.data)
        print("Receive Server IP : "+revice_data["serverip"])
        print("Allow Server IP : "+serverip)
        if revice_data["serverip"] != serverip :
            # print(revice_data["serverip"])
            # print(serverip)
            status_code = flask.Response(status=403)
            return status_code

        action =0
        #for rx1 in relay.relayaction:
        #    action = action + rx1
        for value in revice_data["relay"]:
                gateno = revice_data["relay"][value]["gateno"]  # null
                gateno -= 1
                action =action + relay.relayaction[gateno]
                print (action)

        if action != 0 :
            status_code = flask.Response(status=202)
            return status_code

        #print(request.data)        
        #print(type(revice_data), revice_data)
        #print(revice_data["serverip"])
        status_code = 203
        for value in revice_data["relay"]:
            gateno = revice_data["relay"][value]["gateno"]
            opentime = revice_data["relay"][value]["opentime"]
            waittime = revice_data["relay"][value]["waittime"]
            #nodeName = revice_data["relay"][value]["nodeName"]
            if isinstance(gateno,int) and isinstance(opentime,int) and isinstance(waittime,int):
                node=1
                if doortype=='一般':   #設定一般門和鐵卷門開啟時間
                    dooropentime=5
                else:
                    dooropentime=2

                if (gateno == 1 or gateno ==2) and controlname == 'AR721':



                    t = threading.Thread(target=ar721action, args=(dooropentime,))
                    t.start()

                    
                        

                else:
                    relay.action(gateno,opentime,waittime)
            else: 
                status_code = 204

        rc2 = {"controlip": controlip}
        i = 1
        relay_status = {}
        for rx in relay.relaystatus:
            temp = {str(i) : str(rx)}
            relay_status.update(temp)
            i = i + 1

        rc2.update({"relay": relay_status })
        sensor = relay.read_sensor()
        sensor_status = {}
        i = 1
        yy = {}
        for sx in sensor:
            temp = {str(i): str(sx)}
            sensor_status.update(temp)
            i = i + 1

        rc2.update({"sensor": sensor_status})
        print(rc2)
        response = app.response_class(
            response=json.dumps(rc2),
            status= status_code,
            mimetype='application/json'
        )
        return response
        

    elif request.method == "GET":
        try:
            print(request.args.get('serverip') )
            if request.args.get('serverip').strip() != serverip :
                status_code = flask.Response(status=403)
                return status_code
        except:
            status_code = flask.Response(status=403)
            return status_code

        rc2 = {"controlip": controlip}
        i = 1
        relay_status = {}
        for rx in relay.relaystatus:
            temp = {str(i) : str(rx)}
            relay_status.update(temp)
            i = i + 1

        rc2.update({"relay": relay_status })
        sensor = relay.read_sensor()
        sensor_status = {}
        i = 1
        yy = {}
        for sx in sensor:
            temp = {str(i): str(sx)}
            sensor_status.update(temp)
            i = i + 1

        rc2.update({"sensor": sensor_status})
        print(rc2)
        response = app.response_class(
            response=json.dumps(rc2),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route('/api/v3/remote/control/relay/<int:id>', methods=['GET'])
def api01A(id):
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    urlstring = request.url
    print(token)
    print(request.method)
    if token != token_key:
        status_code = flask.Response(status=401)
        return status_code
        
    if request.method == "GET":      
        rc2 = {"controlip": controlip}
        relay_status = {}
        temp = {str(id) : str(relay.relaystatus[id])}
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
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    urlstring = request.url
    print(token)
    print(request.method)
    if token !=token_key:
        status_code = flask.Response(status=401)
        return status_code
        
    if request.method == "GET":       
        rc2 = {"controlip": controlip}
        sensor = relay.read_sensor()
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


@app.route('/api/v3/remote/control/time', methods=['POST','GET'])
def api02():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    urlstring = request.url
    print(urlstring)
    #print(token)
    #print(token_key)
    print (request.method)
    if token != token_key:
        status_code = flask.Response(status=401)
        return status_code
        
    #revice_data = json.loads(request.data)
    #if revice_data["serverip"] != serverip :
    #    status_code = flask.Response(status=301)
    #    return status_code
        
    if request.method == 'POST':       
        try:
            test = json.loads(request.data)
        except:
            status_code = flask.Response(status=502)
            return status_code

        revice_data = json.loads(request.data)
        print ("serverip:",serverip)
        print (revice_data["serverip"])
        if str(revice_data["serverip"]) != str(serverip) :
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
        if controlname=="AR721":
            node=1
            ser = serial.Serial(sname, baurate, timeout=1)
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
            # print(sysyy,sysmm,sysdd)
            # print(sysww)
            # print(syshh,sysmin,sysss)
            # print('xor=',hex(xor))
            # print('sum=',hex(sum))
            input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
            # print(input)
            ser.write(input)
            sleep(0.2)
            print(controlname,"node=",node, "校時完成")
          
               

        return status_code

    elif request.method == 'GET':
        rc= {"controlip": controlip}
        time.strftime("%Y%m%d%H%M%S", time.localtime())
        rc.update({"Year": time.strftime("%Y", time.localtime())})
        rc.update({"Month": time.strftime("%m", time.localtime())})
        rc.update({"Day": time.strftime("%d", time.localtime())})
        rc.update({"Hour": time.strftime("%H", time.localtime())})
        rc.update({"Minute": time.strftime("%M", time.localtime())})
        rc.update({"Second": time.strftime("%S", time.localtime())})
        response = app.response_class(
            response=json.dumps(rc),
            status=200,
            mimetype='application/json'
        )
        return response
    



@app.route('/api/v3/remote/syns/cards', methods=['POST'])
def apicards():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
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
    else:
        status_code = flask.Response(status=401)
        return status_code


@app.route('/api/v3/remote/syns/booking_customers', methods=['POST'])
def apibooking_customers():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
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
    else:
        status_code = flask.Response(status=401)
        return status_code

@app.route('/api/v3/remote/syns/booking_histories', methods=['POST'])
def apibooking_histories():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
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
    else:
        status_code = flask.Response(status=401)
        return status_code

@app.route('/api/v3/remote/syns/spcards', methods=['POST'])
def apispcards():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
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
    else:
        status_code = flask.Response(status=401)
        return status_code

@app.route('/api/v3/remote/syns/device', methods=['POST'])
def apiDeviceDate():
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
        revice_data = json.loads(request.data)
        conn=sqlite3.connect("cardno.db")
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS device(id TEXT,ip TEXT,local_ip TEXT,ip_mode TEXT,family TEXT,name TEXT,description TEXT,group_id TEXT,mode TEXT,style TEXT,type TEXT,is_booking TEXT,status TEXT,kernel TEXT)')
        c.execute('DELETE FROM device')
        value = revice_data
        c.execute(
            "INSERT INTO device values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                value["id"],
                value["ip"],
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
                value["kernel"]
            )
        )
        conn.commit()
        conn.close()
        status_code = flask.Response(status=203)
        return status_code
    else:
        status_code = flask.Response(status=401)
        return status_code

@app.route('/api/v3/remote/syns/openword', methods=['POST'])
def apiopenword():
    #開門密碼
    token_base64 = request.headers.get('token')
    token = base64.b64decode(token_base64 + "=")
    if token == token_key:
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
        ser = serial.Serial(sname, baurate, timeout=1)
        ser.write(comm)
        sleep(0.2)

    status_code = flask.Response(status=203)
    return status_code
def run():
    app.run(debug=False, use_reloader=False, threaded=False, host="0.0.0.0", port=port)
