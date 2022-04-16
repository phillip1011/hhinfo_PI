import json
import requests
import time
import globals 
import copy


def dcode(uid):
    headers = {'Content-Type': 'application/json'}
    rxstatus = globals._relay.readRelays() 
    sxstatus = globals._relay.readSensors()

    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) +"/api/v1/remote/dcode"
    postdata = {
        'token' : globals._server.token,
        'txcode' : uid,
        'controlip' : str(globals._device.localip) +":" + str(globals._device.localport),
        'gateno' : '1',
        'eventtime' : time.strftime("%Y%m%d%H%M%S", time.localtime()),
        'relays' : rxstatus,
        'sensors' : sxstatus,
        'scanners' : globals._scanner.name
    }
    
    
    # print(request_string)
    try:
        print('呼叫伺服器 : '+api_url_base +' ,postdata : '+json.dumps(postdata))
        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))


        print(response.text)
        print('伺服器回傳狀態:'+str(response.status_code))
        if (response.status_code == 200):
            #print("GET DATA")
            print ('伺服器回傳狀態',response.text)
    except:
        print("Post Dcode error!")
        print("Response text" ,response.text )
      

def report():
    while True:
        time.sleep(10)
        rc = dcode(str(9999099990))


def scode():
    headers = {'Content-Type': 'application/json'}
  
    rxstatus = globals._relay.readRelays()
    sxstatus = globals._relay.readSensors()

    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) +"/api/v1/remote/scode"
    postdata = {
        'token' : globals._server.token,
        'controlip' : str(globals._device.localip) +":" + str(globals._device.localport),
        'gateno' : '1',
        'eventtime' : time.strftime("%Y%m%d%H%M%S", time.localtime()),
        'relays' : rxstatus,
        'sensors' : sxstatus,
        'scanners' : globals._scanner.name
    }
    try:
        print('呼叫伺服器 : '+api_url_base +' ,postdata : '+json.dumps(postdata))
        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))


        print(response.text)
        print('伺服器回傳狀態:'+str(response.status_code))
        if (response.status_code == 200):
            #print("GET DATA")
            print ('伺服器回傳狀態',response.text)
    except:
        print("Post Scode error!")
        print("Response text" ,response.text )

def monitor_sensor():
    while True:
        old_rxstatus = globals._relay.readRelays().copy()
        old_sxstatus = globals._relay.readSensors().copy()

        # print('Relay Status :' , old_rxstatus)
        # print('Relay Sensor :' , old_sxstatus)
        time.sleep(0.5)


        if old_rxstatus != globals._relay.readRelays() or old_sxstatus != globals._relay.readSensors():
            print('tigger scode')
            scode()


