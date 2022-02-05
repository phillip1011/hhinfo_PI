from time import sleep
import serial
from main import ar721_callback
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# ser.flushInput()  # flush input buffer
# ser.flushOutput()  # flush output buffer

# input=b'\x7e\x05\x01\x21\x82\x5d\x01'  #door relay on
# input=b'\x7e\x05\x01\x21\x83\x5c\x01'  #door relay off
# input=b'\x7e\x05\x01\x21\x85\x5a\x01'  #alarm relay on
# input=b'\x7e\x05\x01\x21\x86\x59\x01'  #alarm relay off
def do_read_ar721(sname,baurate):
    ser = serial.Serial(sname, baurate, timeout=1)
    ser.flushInput()  # flush input buffer
    ser.flushOutput()  # flush output buffer
    while True:
        input=b'\x7e\x04\x01\x25\xdb\x01'
        ser.write(input)
        sleep(0.2)
        output = ser.read(64)
        print(output)
        # for data in output:
        #     print(hex(data))
        # print(hex(output[0]))
        # print(hex(output[1]))
        # print(hex(output[2]))
        # print(hex(output[3]))
        # print(hex(output[4]))
        if output==b'':
            print("門口機連線異常")
        else:
            if len(output)>=30:
                if output[3]==0x3 and output[1]==0x1d:
                    UID =  bytearray(b'\x00\x00\x00\x00')
                    UID[0] = output[19]
                    UID[1] = output[20]
                    UID[2] = output[23]
                    UID[3] = output[24]
                    uid = int.from_bytes(UID, byteorder='big')
                    DateTimeString = "20" + str(output[11]) + "-" + str(output[10]) + "-" + str(output[9]) + " " + str(output[7]) + ":" + str(output[6]) + ":" + str(output[5])
                    print('ar721刷卡記錄',uid,DateTimeString)
                    ser.write(b'\x7e\x04\x01\x37\xc9\x01')
                    sleep(0.2)
                    ar721_callback(uid)
                else :
                    ser.write(b'\x7e\x04\x01\x37\xc9\x01')
                    sleep(0.2)
        

if __name__=='__main__':
    #sname='/dev/ttyUSB0'
    sname='/dev/ttyUSB0'
    baurate=9600
    do_read_ar721(sname,baurate)
