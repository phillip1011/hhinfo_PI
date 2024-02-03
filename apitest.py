#!/usr/bin/python3
import json
import requests
#import WebApiClient.login_internet as login_internet 
import sqlite3
#import configparser
import globals
import sound as sound
import os
from time import sleep

def updatedevice():

    request_string = "ip=192.168.50.26:4661"
    headers = {'Content-Type': 'application/json'}
    api_url_base = "http://iiiservice.synology.me/api/v1/data/device"

    try :
        response = requests.get(api_url_base,params=request_string, headers=headers, timeout=3) 
        if response.status_code==200:
            print("Get server/api/v1/data/device 成功")
            r = response.json()
            revice_data = r['data']
            
            if revice_data == None:
                print('無法從伺服器取得Device資料')
                return 0
            print(revice_data)

        else:
            print("Get server/api/v1/data/device 失敗. 伺服器回傳狀態 : ",response.status_code)
    except:
        print("Get server/api/v1/data/device 錯誤.更新Device失敗")

if __name__=='__main__':
    updatedevice()
    

    