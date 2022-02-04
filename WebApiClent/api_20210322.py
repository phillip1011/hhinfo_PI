import flask
import models.relay as relay
from flask import jsonify, request
from flask import send_from_directory,render_template
from multiprocessing import Process

import time
app = flask.Flask(__name__)
app.config["DEBUG"] = False
import threading
clientip = "220.128.141.137"
#localip="172.17.22.138"
server = Process(target=app.run)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello Flask!</h1>"

@app.route('/api/v2/remote/rcode', methods=['GET'])
def api01():
    xxx = None
    urlstring = request.url
    x0 = urlstring.find('?')
    x1 = urlstring.find('&')
    #x2 = urlstring.rfind('&')
    #token = urlstring[x0 +1 :x1-1]
    param = urlstring[x0 + 1:x1]
    serverip = urlstring[x1+1:]
    #print(token,serverip)
    print(param)
    comms = param.split("&rlno")
    print(comms)
    for comm in comms:
        commands = comm.split("&")
        values = []
        names = []
        for para in commands:
            xxx = para.split("=")
            names.append(xxx[0])
            xxx[1] = xxx[1].replace(' ', '')
            try:
                values.append(int(xxx[1]))
            except:
                values.append(0)
        if (len(values) < 3 ):
            values.append(0)
        if (len(values) < 3):
            values.append(0)
        relay.action(values[0], values[1], values[2])
        print(names)
        print(values)

    return rcode_return (token,serverip)


def rcode_return(token,serverip):
    sxstatus = relay.read_sensor()
    rxstatus = relay.relaystatus
    request_string = serverip + "&"
    request_string += "controlip=" + clientip
    for i in range(4):
        request_string += "&r" + str(i + 1) + "status=" + str(rxstatus[i])
    for i in range(6):
        request_string += "&s" + str(i + 1) + "status=" + str(sxstatus[i])
    print(request_string)
    return request_string


@app.route('/api/v2/remote/get', methods=['GET'])
def api02():
    xxx = None
    urlstring = request.url
    x0 = urlstring.find('?')
    x1 = urlstring.find('&')
    #x2 = urlstring.rfind('&')
    #token = urlstring[x0 + 1:x1 - 1]
    param = urlstring[x0 + 1:x1]
    print(x0,x1)
    serverip = urlstring[x1 + 1:]
    print ("get  param = " + param)
    command = param[0:7]
    print (command)
    if command == "getr=al":
        print("revice get all")
        request_string =  serverip + "&"
        request_string += "controlip=" + clientip
        sxstatus = relay.read_sensor()
        rxstatus = relay.relaystatus
        for i in range(4):
            request_string += "&r" + str(i + 1) + "status=" + str(rxstatus[i])
        for i in range(6):
            request_string += "&s" + str(i + 1) + "status=" + str(sxstatus[i])
        print(request_string)
        return request_string
    elif command == "gettime" :
        print("revice get time ")
        request_string = serverip + "&"
        request_string += "controlip=" + clientip + "&"
        request_string += "nowtime=" + time.strftime("%Y%m%d%H%M%S", time.localtime())
        print(request_string)
        return request_string
    elif command == "settime" :
        print("revice get set time")
        request_string = serverip + "&"
        request_string += "controlip=" + clientip + "&"
        request_string += "status=0"
        print(request_string)
        ss="serverip=35.221.198.141&controlip=220.128.141.136&r1status=0&r2status=0&r3status=0&r4status=0&s1status=0&s2status=0&s3status=0&s4status=0&s5status=0&s6status=0"
        #return request_string
        return render_template('result.html',user_template=ss)
        server.terminate()
        server.join()
    else :  
        print("no action")
        return serverip
     

def run():
    #app.run(debug=False, use_reloader=False, threaded=True, host="0.0.0.0" , port=4661)
    server = Process(target=app.run(debug=False, use_reloader=False, threaded=True, host="0.0.0.0" , port=4661))

    server.start()

