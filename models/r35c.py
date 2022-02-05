from time import sleep
import serial
#import models.serial_name as serial_name
from datetime import datetime
#import serial_name as serial_name

com_error = 0
#usb_names=["usb 1-1.1.3"]
sname = '/dev/ttyUSB0'
ser = serial.Serial(sname, 9600, timeout=1)
#node = b'\x01'

def string_hex(str1):
    an_integer = int(hex_string, 16)
    hex_value = hex(an_integer)
    print(hex_value)

def decode(datas):
    #print (datas,"AAA")
    i=0
    sn=''
    for data1 in datas:
        print(i,data1)
        if (data1 == 2):
            uid = (datas[i+1:i+11]).decode("utf-8") 

            break
        i =i +1
    return str(uid)

def getdata():
    if com_error == 1 :
        return 
    # 清空 READ BUFFER
    output=''
    try:   
        output = ser.readline()
    except:
        print("error")
        comerror = 1 
        ser.close()
        # 回報讀卡機錯誤
        
    #print(output)
    if len(output) == 0: 
        return ''
    print(output)
    if  len(output) > 10  :        
        return  output
    else: 
        #print("read error or end ")
        output =''
        return output

def get_event():
    output = getdata()
    #print(output)
    try:
        uid = decode(output)
        print( uid)
#--------------------------------------modify by phillip 將刷卡卡號寫入inputcardlog.txt
        # cardno = uid
        # #cardno  = "1234567890"
        # timenow =str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # text_file = open("/home/ubuntu/nfc/inputcardlog.txt", "a+")
        # text_file.write(timenow+" "+str(cardno+'\n'))
        # print(timenow +" Input CARD ="+str(cardno))
        # text_file.close()
#--------------------------------------
        return uid
    except:
        return ''

def do_read_r35c(no,r35c_callback = None):
    com_error = 0
    while True:
        uid = get_event()
        if uid != '' :
            #print(uid)
            if (r35c_callback != None):
                #print(datestring,uid)
                #uid = int(uid)
                r35c_callback(uid)
        sleep(1)

if __name__=='__main__':
    do_read_r35c('',None)

