import json
import requests
import time
import models.relay as relay

#serverip = "localhost"
serverip = "10.8.0.1"
#port = 44372
port = 80
localport =4661
def dcode(token, uid, clientip,gateno,rxstatus,sxstatus):
    port = 8080
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
        for node in range(1,ar721cnt+1):
            request_string += "&"+"scannernode" + str(node)+"=" + str(node)

    # print(request_string)
    try:
        response = requests.get(api_url_base, params=request_string, headers=headers, verify=False,timeout=5)
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

def report(clientip,txcode,token):
    while True:
        time.sleep(15)
        #time.sleep(60*3)
        #token = "aGhpbmZvOjIwMjAwMTE2MjIxMDM5"
        rxstatus = relay.relaystatus 
        sxstatus = relay.read_sensor()
        #sxstatus = [0, 0, 0, 0, 0, 0]
        rc = dcode(token, str(txcode), clientip, 1, rxstatus, sxstatus)
        if (rc == b'\x01'):
            dcode(token, str(txcode), clientip, 1, rxstatus, sxstatus)

def operdo(token, clientip,status):
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) +"/api/v1/remote/operdo"
    request_string = "token=" + token + "&"
    request_string += "controlip=" + clientip +":" + str(localport) + "&"
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
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://" + serverip + ":" + str(port) +"/api/v1/remote/scode"

    request_string = "controlip=" + clientip + ":" + str(localport)  + "&"
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

def monitor_sensor(clientip,token):
    sxstatus = [0,0,0,0,0,0]
    rxstatus = [0,0,0,0]
    while True:
        time.sleep(0.5)
        #print (sxstatus)
        #print(relay.read_sensor())
        if (sxstatus != relay.read_sensor()):
            rxstatus = relay.relaystatus
            sxstatus = relay.read_sensor()
            scode(clientip,rxstatus,sxstatus)
        if (rxstatus != relay.relaystatus):
            rxstatus = relay.relaystatus
            sxstatus = relay.read_sensor()
            scode(clientip,rxstatus,sxstatus)

        #rxstatus = relay.relaystatus
        # xx= relay.read_hand()
        # #print(xx,rxstatus)
        # if (xx[0] == 0):
        #     #if rxstatus[0] == 0:
        #     relay.do_action(1,4,0)

