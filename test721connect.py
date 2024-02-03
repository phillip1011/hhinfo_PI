from time import sleep
import serial
from datetime import datetime
#
def cardnbr(output):


    UID =  bytearray(b'\x00\x00\x00\x00')
    UID[0] = output[7]
    UID[1] = output[8]
    UID[2] = output[9]
    UID[3] = output[10]
    uid = int.from_bytes(UID, byteorder='big')
    uid=str(uid).zfill(10)
    print("MyUID is ",uid)


def write_command_to_node(node, func):
    xor=255^node^int(func,16)
    sum=node+int(func,16)+xor
    sum =sum % 256
    comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
    try:
        ser = serial.Serial("/dev/485_USB", 9600, timeout=1)
        ser.flushInput()  # flush input buffer
        ser.flushOutput()  # flush output buffer
        ser.write(comm)
        sleep(0.2)
        output = ser.read(64)
        if len(output)==14:
            cardnbr(output)
        


        print("測試USB連線721狀態")
        print("721回傳資料內容:",output)
        print("721回傳資料長度:",len(output),"(正常值=10)")
    except:
        print("USB連線卡機失敗")    


write_command_to_node(1, '0x13')
