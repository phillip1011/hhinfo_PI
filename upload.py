import json
import requests
import sqlite3
import globals


def uploadlog():
    try:
        headers = {'Content-Type': 'application/json'}
        path = '/api/v1/data/log'
        api_url_base = "http://" + globals._server.serverip + ":" + str(globals._server.serverport) + path
    
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
                "auth" : row[4],
                "process" :row[5],
                "result" : row[6]
            }
            data.append(temp_obj)
            cnt+=1
            # print(temp_obj)        
        postdata = {
            'ip' : globals._device.localip+ ":" + str(globals._device.localport),
            'data' :data
        }

        response = requests.post(api_url_base,headers=headers,  data=json.dumps(postdata))
        #print(response.json())
        if cnt!=0:
            if response.status_code==200:
                print("刷卡資料上傳伺服器成功,共",cnt,"筆")
                c.execute('update scanlog set rtnflag=1 where rtnflag=0')
            else:
                print("刷卡資料上傳失敗")
        else:
            print("無刷卡上傳資料")
        conn.commit()
        conn.close()
    except:
        print("Post data log error!")
        print("Response text" ,response.text )


