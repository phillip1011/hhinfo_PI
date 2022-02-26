import RPi.GPIO as GPIO
import time
import models.relay as relay


relaystatus = [0, 0, 0, 0]
LED_PIN = [5,6,13,16]  #5,6,13,16,19,20,21,26
SEN_PIN = [17, 27, 22, 17, 27, 22] #17,27,22,12,23,24,25,18
HAND_PIN= [12,12]
relayaction = [0, 0, 0, 0]
GPIO.setmode(GPIO.BCM)

for i in range(4):
    GPIO.setup(LED_PIN[i], GPIO.OUT )
for i in range(6):
    GPIO.setup(SEN_PIN[i], GPIO.IN)
for i in range(2):
    GPIO.setup(HAND_PIN[i], GPIO.IN)

GPIO.output(5, 0)  #參數0=on , 參數1=off

print(LED_PIN)
rxstatus = relay.relaystatus 
print(rxstatus)
