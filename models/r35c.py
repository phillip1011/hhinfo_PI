from time import sleep
import serial
from datetime import datetime
import chkcard as chkcard
import WebApiClient.remote as remote
import globals
com_error = 0



def callback(uid):
    print('-----getcallback-------'+str(uid))
    if uid != '' :
        uid =str(uid).zfill(10)
        chkcard.chkcard(uid)
    else:
        print("read nfc error")


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
        ser = serial.Serial(globals._scanner.sname,globals._scanner.baurate, timeout=1)
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

def do_read_r35c():
    while True:
        uid = get_event()
        if uid != '' :
            callback(uid)
        # sleep(0.2)




# if __name__=='__main__':
#     do_read_r35c('',None)

