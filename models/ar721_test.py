# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from time import sleep
import serial

node = b'\x01'
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def incode(data):
    xor = 255
    sum = 0
    for x in data:
        xor = xor ^ x
        sum = sum + x
    sum = sum + xor
    sum =sum % 256
    rc = b'\x7E' + bytes([len(data)+2])
    rc = rc + data + bytes([xor]) + bytes([sum])
    return rc

def decode_ar721_event(data):
    if data[0] != 126:
        return '', 0
    len1 = data[1];
    if (len(data) != len1 + 2):
         return '', 1
    if (data[3] == 4):
        return '', 4
    if (data[3] == 3 or data[3] == 12):
        DateTimeString = "20" + str(data[11]) + "/" + str(data[10]) + "/" + str(data[9]) + " " +\
                     str(data[7]) + ":" + str(data[6]) + ":" + str(data[5]);
        UID =  bytearray(b'\x00\x00\x00\x00')
        UID[0] = data[19]
        UID[1] = data[20]
        UID[2] = data[23]
        UID[3] = data[24]
        sn = int.from_bytes(UID, byteorder='big')
        return DateTimeString,sn;

def std_command(comm):
    # 清空 READ BUFFER
    ser.flushInput()  # flush input buffer
    ser.flushOutput()  # flush output buffer
    input = incode(comm)
    ser.write(input)
    sleep(0.2)
    output = ser.read(64)
    return output

def ar721_get_event():
    comm = node + b'\x25'
    output = std_command(comm)
    print(output)
    try:
        datestring , uid = decode_ar721_event(output)
        #print(datestring, uid)
        comm = node + b'\x37'
        output = std_command(comm)
        return datestring , uid
    except:
        return '',0
def do_read_ar721(no1):
    node = no1
    while True:
        datestring, uid = ar721_get_event()
        if (uid != 0 and  uid != 1 and uid != 4) : 
            print('result:',datestring,uid)           
            # if (ar721_callback != None):
            #     print(datestring,uid)
            #     ar721_callback(datestring, uid)

# Press the green button in the gutter to run the script.
def init():
    #print_hi('PyCharm')
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ar721_get_event()

do_read_ar721(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
