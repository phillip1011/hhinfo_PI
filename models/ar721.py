from time import sleep
import serial
from datetime import datetime
import chkcard as chkcard
import WebApiClient.remote as remote
import globals
import ResetUSB as ResetUSB

def callback(uid):
    print("__________do_read_ar721________________")
    uid =str(uid).zfill(10)
    chkcard.chkcard(uid)


def write_command_to_node(node, func):
    xor=255^node^int(func,16)
    sum=node+int(func,16)+xor
    sum =sum % 256
    comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
    try:
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(comm)
    except:
        print("ser連接USB失敗")
    sleep(0.2)
    
def do_read_ar721():
    # ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
    # ser.flushInput()  # flush input buffer
    # ser.flushOutput()  # flush output buffer
    nodesCount = globals._scanner.nodesCount
    while True:
       for x in range(nodesCount):
            try:
                ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
                ser.flushInput()  # flush input buffer
                ser.flushOutput()  # flush output buffer
                node = x+1
                write_command_to_node(node, '0x25')
                output = ser.read(64)
            except:
                print(globals._scanner.sname + ' AR721 node:' + str(node) + ' read error')
                sleep(3)
            if len(output)==31:
                today=str(datetime.now().strftime('%Y-%m-%d'))
                ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
                ScanTime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)
                if today==ScanDate:
                    if output[3]==0x3 and output[1]==0x1d:
                        UID =  bytearray(b'\x00\x00\x00\x00')
                        UID[0] = output[19]
                        UID[1] = output[20]
                        UID[2] = output[23]
                        UID[3] = output[24]
                        uid = int.from_bytes(UID, byteorder='big')
                        print('AR721刷卡記錄,站號(node)=',node,'卡號:',uid,'刷卡日期',ScanDate,'刷卡時間',ScanTime)
                        write_command_to_node(node, '0x37')
                        sleep(0.2)
                        callback(uid)
                    else :
                        write_command_to_node(node, '0x37')
                        sleep(0.2)
                else:
                    print("讀卡機或主機時間不符,",'讀卡機刷卡日期:',ScanDate,ScanTime,'系統時間:',today)
                    write_command_to_node(node, '0x37')
            elif len(output)==0 :
                ResetUSB.ResetUSB()
                sleep(2)
