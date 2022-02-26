import serial
from time import sleep
from datetime import datetime
import struct

sname='/dev/ttyUSB0'
baurate=9600
ser = serial.Serial(sname, baurate, timeout=1)
def ar721comm(node,func,data):
    xor=255^node^int(func,16)^int(data,16)
    sum=node+int(func,16)+int(data,16)+xor
    sum =sum % 256
    print('xor=',hex(xor))
    print('sum=',hex(sum))
    comm=b'\x7e\x05'+ bytes([node])+ bytes([int(func,16)])+bytes([int(data,16)]) + bytes([xor])+ bytes([sum])
    
    # ser.write(comm)
    # sleep(0.2)
    return comm

def scode(node,func):
    xor=255^node^int(func,16)
    sum=node+int(func,16)+xor
    sum =sum % 256
    # print(xor)
    # print(sum)
    comm=b'\x7e\x04'+ bytes([node])+ bytes([int(func,16)]) + bytes([xor])+ bytes([sum])
    ser.write(comm)
    sleep(0.2)
def rtime():
    today=str(datetime.now().strftime('%Y-%m-%d'))
    time=str(datetime.now().strftime('%H:%M:%S'))
    print('系統時間=',today,time)
    output = ser.read(64)
    ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
    Scantime = str(output[7]).zfill(2) + ":" + str(output[6]).zfill(2) + ":" + str(output[5]).zfill(2)
    print("控制器時間=",ScanDate,Scantime)

def test():
    ar721cnt=0
    for node in range(1,5):
        xor=255^node^37
        sum=(node+37+xor)
        sum =sum % 256
        input=b'\x7e\x04'+ bytes([node])+ b'\x25' + bytes([xor])+ bytes([sum])
        ser.write(input)
        sleep(0.2)
        output=ser.read(64)
        try:
            hex(output[0])=='0x7e'
            ar721cnt +=1
            print("check AR7221 node=",node,"sucess")
        except:
            print("check AR7221 node=",node,"fail")
    # for i in range(1,ar721cnt+1):
    #     print(i)

    sysyy=int(datetime.now().strftime('%y'))
    sysmm=int(datetime.now().strftime('%m'))
    sysdd=int(datetime.now().strftime('%d'))
    syshh=int(datetime.now().strftime('%H'))
    sysmin=int(datetime.now().strftime('%M'))
    sysss=int(datetime.now().strftime('%S'))
    sysww=int(datetime.now().strftime('%w'))
    if sysww==0:
        sysww=7
    for node in range(1,ar721cnt+1):
        print("mynode=",node)
        # xor=255^node^23^sysss^sysmin^syshh^sysww^sysdd^sysmm^sysyy
        # sum=(node+23+sysss+sysmin+syshh+sysww+sysdd+sysmm+sysyy+xor)
        # if sum>256:
        #     sum -=256
        # print(sysyy,sysmm,sysdd)
        # print(sysww)
        # print(syshh,sysmin,sysss)
        # print('xor=',hex(xor))
        # print('sum=',hex(sum))
        # input=b'\x7e\x0B'+ bytes([node])+ b'\x23' + bytes([sysss]) + bytes([sysmin])+ bytes([syshh])+ bytes([sysww])+ bytes([sysdd])+ bytes([sysmm])+ bytes([sysyy])+ bytes([xor])+ bytes([sum])
        # print(input)
        # ser.write(input)
        # sleep(0.2)

        xor=255^node^36     #commd 24 => 36十進位
        sum=(node+36+xor)
        sum =sum % 256
        print(node,"xor=",xor)     #DA=218   , D9=217
        print(node,"sum=",sum)
        input=b'\x7e\x04'+ bytes([node])+ b'\x24'+ bytes([xor])+ bytes([sum])
        ser.write(input)
        sleep(0.2)
        output = ser.read(64)
        ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
        print(ScanDate)
        # print("AR721","node=",node, "校時成功")
def test5():
    node='1'
    func='0x83'
    addr='00001'
    site='01089'
    card='59979'
    PIN='1234'
    
    addrH=struct.pack(">H",int(addr))
    addrH=addrH[0]
    addrL=struct.pack(">H",int(addr))
    addrL=addrL[1]

    siteH=struct.pack(">H",int(site))
    siteH=siteH[0]
    siteL=struct.pack(">H",int(site))
    siteL=siteL[1]

    cardH=struct.pack(">H",int(card))
    cardH=cardH[0]
    cardL=struct.pack(">H",int(card))
    cardL=cardL[1]

    pinH=struct.pack(">H",int(PIN))
    pinH=pinH[0]
    pinL=struct.pack(">H",int(PIN))
    pinL=pinL[1]

    #xor=0xff^node^int(func,16)^0x00^0x1^0x4^0x41^0xea^0x4b^0x4^0xd2^0x2^0x1
    xor=0xff ^ int(node,16) ^ int(func,16) ^ addrH ^ addrL ^ siteH ^ siteL ^ cardH ^ cardL ^ pinH ^ pinL ^ 0x2 ^ 0x1
    sum=int(node,16) + int(func,16) + addrH + addrL + siteH + siteL + cardH + cardL + pinH + pinL + 0x2 + 0x1 + xor
    sum =sum % 256
    # print('xor=',hex(xor))
    # print('sum=',hex(sum))
    comm=(
        b'\x7e\x0e'+ 
        bytes([int(node,16)])+ 
        bytes([int(func,16)])+ 
        bytes([addrH])+
        bytes([addrL])+
        bytes([siteH])+
        bytes([siteL])+
        bytes([cardH])+
        bytes([cardL])+
        bytes([pinH])+
        bytes([pinL])+
        b'\x02\x01' + 
        bytes([xor])+ 
        bytes([sum])
    )

    ser = serial.Serial(sname, baurate, timeout=1)
    ser.write(comm)
    sleep(0.2)


test5()
# scode(2,'0x24')
# rtime()
# test=ar721comm(1,'0x21','0x83')
# print(test)