import threading
import serial
import sqlite3
from time import sleep
from datetime import datetime

def getdata():
    com_error = 0
    sname = '/dev/ttyUSB0'
    ser = serial.Serial(sname, 9600, timeout=1)
    if com_error == 1 :
        print("quit")
        return 
    # 清空 READ BUFFER
    output=''
    try:   
        output = ser.readline()
    except:
        ser.close()
    if len(output) == 0: 
        return ''

    if  len(output) > 10  :        
        print("字串長度=" + str(len(output)))
        return output
    else: 
        output =''
        return output
    ser.close()

def decode(datas):
    i=0
    for data1 in datas:     #例如字串: b'\x024077189990\r\n' 第1個字母直到2, 取10位
        print(data1)
        if (data1 == 2):
            uid = (datas[i+1:i+11]).decode("utf-8") 
            break
        i =i +1
    return str(uid)

def get_event():    
    output = getdata()
    try:
        uid = decode(output)
#----------- modify by phillip 將刷卡卡號寫入  scanlog           inputcardlog.txt
        conn=sqlite3.connect("cardno.db")
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scanlog(cardnbr TEXT,date TEXT,time TEXT,rtnflag TEXT)')
        today=str(datetime.now().strftime('%Y%m%d'))
        time=str(datetime.now().strftime('%H%M%S'))
        c.execute("INSERT INTO scanlog VALUES("+ str(uid) + ","+ today+","+time+",0)")
        conn.commit()
        conn.close()
        
        cardno = uid   #cardno  = "1234567890"
        timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        text_file = open("/home/ubuntu/nfc/inputcardlog.txt", "a+")
        text_file.write(timenow+" "+str(cardno+'\n'))
        print(timenow +" Input CARD ="+str(cardno))
        text_file.close()
#-----------
        return uid
    except:
        return ''

def do_read_r35c():
    while True:
        uid = get_event()
        sleep(0.7)

# if __name__=='__main__':
#     t_scan = threading.Thread(target=do_read_r35c())
#     t_scan.setDaemon(True)
#     t_scan.start()