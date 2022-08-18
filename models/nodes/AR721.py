from time import sleep
import serial
from datetime import datetime
import chkcard as chkcard
import WebApiClient.remote as remote
import globals

class AR721:
    sname = ''
    baurate = ''
    nodesCount = 1

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.token = cf.get("ServerConfig", "token")
        self.token_key = cf.get("ServerConfig", "token_key")
        self.serverip = cf.get("ServerConfig", "serverip")
        self.serverport = cf.get("ServerConfig", "serverport")
        self.VPNserverip = cf.get("ServerConfig", "VPNserverip")
        self.verifyserverip = cf.get("ServerConfig", "verifyserverip")
        self.forceVPN = cf.get("ServerConfig", "forceVPN")
        self.show()


    def OpenDoor(node):
        print('openDoor')
        AR721_R1_ON = commandTransaction(node,'0x21','0x82')   #door relay on
        AR721_R1_OFF = commandTransaction(node,'0x21','0x83')  #door relay off
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.write(AR721_R1_ON)
        sleep(globals._device.opendoortime)
        ser.write(AR721_R1_OFF)

        globals._relay.action(1,globals._device.opendoortime,0)
        for relay in relays:
            openRelay(int(relay))
    
    def CloseDoor():


    def writeCommand():




    def commandTransaction(node, func, data = None):
        xor=255^node^int(func,16)
        if data:
            xor=xor^int(data,16)
        sum=node+int(func,16)+xor
        if data:
            sum=sum+int(data,16)
        sum =sum % 256
        comm=b'\x7e\x05'+ bytes([node])+ bytes([int(func,16)])
        if data:
            comm=comm+bytes([int(data,16)])
        comm=comm+bytes([xor])+ bytes([sum])
        return comm

    def decodeUid(output):
        uid = ''
        if len(output)==31:
            today=str(datetime.now().strftime('%Y-%m-%d'))
            ScanDate = "20" + str(output[11]).zfill(2) + "-" + str(output[10]).zfill(2) + "-" + str(output[9]).zfill(2)
            if today==ScanDate:
                if output[3]==0x3 and output[1]==0x1d:
                    UID =  bytearray(b'\x00\x00\x00\x00')
                    UID[0] = output[19]
                    UID[1] = output[20]
                    UID[2] = output[23]
                    UID[3] = output[24]
                    uid = int.from_bytes(UID, byteorder='big')
        return uid

        
    def doRead():
        ser = serial.Serial(globals._scanner.sname, globals._scanner.baurate, timeout=1)
        ser.flushInput()  # flush input buffer
        ser.flushOutput()  # flush output buffer
        nodesCount = globals._scanner.nodesCount
        while True:
            for x in range(nodesCount):
                node = x+1
                writeCommand(commandTransaction(node, '0x25'))
                try:
                    output = ser.read(64)
                    uid = decodeUid(output)
                    if uid != '':
                        chkcard.verifycard(uid)
                   
                except:
                    print('read error')
                writeCommand(commandTransaction(node, '0x37'))