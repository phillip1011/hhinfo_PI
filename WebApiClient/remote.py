import json
import requests
import time
import models.relay as relay

#serverip = "localhost"
# serverip = "10.8.0.1"
# #port = 44372
# port = 80
# localport =4661


def backupdcode(token, uid, clientip,gateno,rxstatus,sxstatus):
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) +"/api/v1/remote/dcode"
    request_string = "token=" + token + "&"
    request_string += "txcode=" + uid + "&"
    request_string += "controlip=" + str(clientip) +":" + str(localport) + "&"
    request_string += "gateno=" +str(gateno) + "&"
    request_string += "eventtime=" + time.strftime("%Y%m%d%H%M%S", time.localtime())
    # print(request_string)
    for i in range(4):
        request_string += "&r" + str(i+1) + "status=" + str(rxstatus[i])
    for i in range(6):
        request_string += "&s" + str(i+1) + "status=" + str(sxstatus[i])
    # print(api_url_base + "?" + request_string)
    if scannername=='AR721':
        request_string += "&"+"scannername="+str(scannername)
      

    # print(request_string)
    try:
        response = requests.get(api_url_base, params=request_string, headers=headers, verify=False,timeout=5)
        print(response.text)
        print('伺服器回傳狀態:'+str(response.status_code))
        if (response.status_code ==200):
            #print("GET DATA")
            print ('伺服器回傳狀態',response.text)
            if uid != b'9999090000':
                return response.text
            else:
                print("SEND　REPORT ")
                return b'\x00'
        else:
            print("GET DATA STATUS ERROR !")
            return b'\x01'
    except:
        print("GET DATA CONNECT ERROR !")
        return b'\x01'
    else:
        return b'\x01'
    #response = requests.get(api_url_base, params=query)

def dcode(token, uid, clientip,gateno,rxstatus,sxstatus):
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + _server.serverip + ":" + str(_server.serverport) +"/api/v1/remote/dcode"
    postdata = {
        'token' : token,
        'txcode' : uid,
        'controlip' : str(_device.localip) +":" + str(_device.localport),
        'gateno' : str(gateno),
        'eventtime' : time.strftime("%Y%m%d%H%M%S", time.localtime()),
        'relays' : rxstatus,
        'sensors' : sxstatus,
        'scanners' : _scanner.name
    }
    
    
    # print(request_string)
    try:
        print('呼叫伺服器 : '+api_url_base +' ,postdata : '+json.dumps(postdata))
        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))


        print(response.text)
        print('伺服器回傳狀態:'+str(response.status_code))
        if (response.status_code ==200):
            #print("GET DATA")
            print ('伺服器回傳狀態',response.text)
            if uid != b'9999090000':
                return response.text
            else:
                print("SEND　REPORT ")
                return b'\x00'
        else:
            print("GET DATA STATUS ERROR !")
            return b'\x01'
    except:
        print("GET DATA CONNECT ERROR !")
        return b'\x01'
    #response = requests.get(api_url_base, params=query)

def report(_server,_device):
    while True:
        time.sleep(10)
        #time.sleep(60*3)
        #token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"
        rxstatus = relay.relaystatus 
        sxstatus = relay.read_sensor()
        #sxstatus = [0, 0, 0, 0, 0, 0]
        rc = dcode(_server.token, str(9999099990), _device.localip, 1, rxstatus, sxstatus)
        if (rc == b'\x01'):
            dcode(_server.token, str(9999099990), _device.localip, 1, rxstatus, sxstatus)

def operdo(token, clientip,status):
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + _server.serverip + ":" + str(_server.serverport) +"/api/v1/remote/operdo"
    request_string = "token=" + token + "&"
    request_string += "controlip=" + _device.localip +":" + str(_device.localport) + "&"
    request_string += "status=" +str(status)
    try:
        response = requests.get(api_url_base, params=request_string, headers=headers, verify=False,timeout=5)
        if (response.status_code == 200):
            print("send status")
        else:
            print("SEND STATUS ERROR !")
    except:
        print("SEND STATUS CONNECT ERROR !")

def scode(clientip,rxstatus,sxstatus):
    print('_____')
    print(_server)
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + _server.serverip + ":" + str(_server.serverport) +"/api/v1/remote/scode"

    request_string = "controlip=" + _device.localip + ":" + str(_device.localport)  + "&"
    request_string += "eventtime=" + time.strftime("%Y%m%d%H%M%S", time.localtime())
    for i in range(4):
        request_string += "&r" + str(i+1) + "status=" + str(rxstatus[i])
    
    for i in range(6):
        request_string += "&s" + str(i+1) + "status=" + str(sxstatus[i])

    #request_string += "status=" +str(status)
    try:
        #print(api_url_base + "?" + request_string)
        response = requests.get(api_url_base, params=request_string, headers=headers, verify=False,timeout=5)
        if (response.status_code == 200):
            print("scode send status")
        else:
            print("SEND SENSOR STATUS ERROR !")
    except:
        print("SEND STATUS CONNECT ERROR !")

def monitor_sensor(_server,_device):
    sxstatus = [0,0,0,0,0,0]
    rxstatus = [0,0,0,0]
    while True:
        time.sleep(0.5)
        #print (sxstatus)
        #print(relay.read_sensor())
        if (sxstatus != relay.read_sensor()):
            rxstatus = relay.relaystatus
            sxstatus = relay.read_sensor()
            scode(_device.localip,rxstatus,sxstatus)
        if (rxstatus != relay.relaystatus):
            rxstatus = relay.relaystatus
            sxstatus = relay.read_sensor()
            scode(_device.localip,rxstatus,sxstatus)

        #rxstatus = relay.relaystatus
        # xx= relay.read_hand()
        # #print(xx,rxstatus)
        # if (xx[0] == 0):
        #     #if rxstatus[0] == 0:
        #     relay.do_action(1,4,0)

