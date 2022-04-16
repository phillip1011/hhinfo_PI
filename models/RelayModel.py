import RPi.GPIO as GPIO
import configparser
import json
import time
import threading

class RelayModel:
    relayPins = ''
    sensorPins = ''

    
    
  
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("/home/ubuntu/hhinfo_PI/config.ini")
        self.relayPins = json.loads(cf.get("RelayConfig", "relayPins"))
        self.sensorPins = json.loads(cf.get("RelayConfig", "sensorPins"))
        self.show()
        self.setupGPIO()
    
    def show(self):
        print("__________RelayModel show__________")
        print("relayPins = " , self.relayPins)
        print("sensorPins = " , self.sensorPins)

    def initRelay(self):
        GPIO.output(self.relayPins, 1)

    def setupGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relayPins , GPIO.OUT)
        GPIO.setup(self.sensorPins , GPIO.IN)
       

    def openGPIOPin(self,pinNumber):
        print('開啟 GPIO Pin腳 : '+ str(pinNumber))
        GPIO.output(pinNumber, 0)
        self.readGPIOPinStatus(pinNumber)

    def closeGPIOPin(self,pinNumber):
        print('關閉 GPIO Pin腳 : '+ str(pinNumber))
        GPIO.output(pinNumber, 1)
        self.readGPIOPinStatus(pinNumber)


    def readGPIOPinStatus(pinNumber):
        if GPIO.input(pinNumber) == 1:
            print("檢查 GPIO Pin腳 : " +str(pinNumber) + " 關閉")
        else:
            print("檢查 GPIO Pin腳 : " +str(pinNumber) + " 開啟")


    def readSensors(self):
        xx = []
        for i in self.sensorPins:
            x = GPIO.input(i)
            if(x == 1):
                xx.append(0)
            else: 
                xx.append(1)
        print('readSensors : ',xx)
        return xx


    def readRelays(self):
        xx = []
        for i in self.relayPins:
            x = GPIO.input(i)
            if(x == 1):
                xx.append(0)
            else: 
                xx.append(1)
        print('readRelays : ',xx)
        return xx 
    
    
    def actionJob(self,relayIndex,opentime,waittime):
        pinNumber = self.relayPins[relayIndex]
        if waittime != 0:
            time.sleep(waittime)
        if opentime <= 0:
            self.closeGPIOPin(pinNumber)
            return
        self.openGPIOPin(pinNumber)

        if opentime<255:
            time.sleep(opentime)
            self.closeGPIOPin(pinNumber)

    def action(self,relayIndex,opentime,waittime):
        if relayIndex <= 0 :
            return
        relayIndex = relayIndex-1
        t = threading.Thread(target=self.actionJob, args=(relayIndex, opentime, waittime))
        t.start()


      
        
