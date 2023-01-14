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
        'scanners' : globals._scanner.scannerName
    }
    
    
    # print(request_string)
    try:
        #print('呼叫伺服器 : '+api_url_base +' ,postdata : '+json.dumps(postdata))
        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata), timeout=3)
        #print(response.text)
        #print('伺服器回傳狀態:'+str(response.status_code))
        #if (response.status_code == 200):
            #print("GET DATA")
            #print ('伺服器回傳狀態',response.text)
    except:
        print("Post Dcode error!")
    
      

def report():
    while True:
        time.sleep(180)
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
        'scanners' : globals._scanner.scannerName
    }
    try:
        #print('呼叫伺服器 : '+api_url_base +' ,postdata : '+json.dumps(postdata))
        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata), timeout=3)


        print(response.text)
        print('伺服器回傳狀態:'+str(response.status_code))
        if (response.status_code == 200):
            #print("GET DATA")
            print ('伺服器回傳狀態',response.text)
    except:
        print("Post Scode error!")


def monitor_sensor():
    while True:
        old_rxstatus = globals._relay.readRelays().copy()
        old_sxstatus = globals._relay.readSensors().copy()

       
        # print('Relay Old Status :' , old_rxstatus)
        # print('Sensor Old Status :' , old_sxstatus)
        time.sleep(0.5)

        new_rxstatus = globals._relay.readRelays().copy()
        new_sxstatus = globals._relay.readSensors().copy()

        # print('Relay New Status :' , new_rxstatus)
        # print('Sensor New Status :' , new_sxstatus)

        if old_rxstatus != new_rxstatus or old_sxstatus != new_sxstatus:
            if old_sxstatus[3] == 0 and new_sxstatus[3] == 1 :
                globals._relay.action(1,globals._device.opendoortime,0)
            print('tigger scode')
            scode()


