import json
import requests
import sqlite3
import globals
from time import sleep

def getLogData():
    data = []
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    c.execute('select * from scanlog where rtnflag=0')
    for row in c:
        temp_obj = {
            "cardnbr": row[0],
            "date" : row[1],
            "time" : row[2],
            "auth" : row[4],
            "process" :row[5],
            "result" : row[6]
        }
        data.append(temp_obj)
    conn.commit()
    conn.close()  
    return data

def updateLogStatus():
    conn=sqlite3.connect("/home/ubuntu/hhinfo_PI/cardno.db")
    c=conn.cursor()
    rr = c.execute('update scanlog set rtnflag=1 where rtnflag=0')
    conn.commit()
    conn.close()
    return rr.rowcount


def uploadlog():
    headers = {'Content-Type': 'application/json'}
    path = '/api/v1/data/log'
    api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) + path
   
    while True:
        try :
            postdata = getLogData()

            if len(postdata) != 0 :
                postdata = {
                    'ip' : globals._device.localip+ ":" + str(globals._device.localport),
                    'data' :postdata
                }
                response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata), timeout=3)
                if response.status_code==200:
                    updateRows = updateLogStatus()
                    print("刷卡資料上傳伺服器成功 更新" +str(updateRows) +"筆") 
                
                else:
                    print("刷卡資料上傳失敗,伺服器回傳狀態 : ",response.status_code)
            #else:
                #print("無刷卡上傳資料")
            
        except:
            print("Post data log error.")
        sleep(60*1)


