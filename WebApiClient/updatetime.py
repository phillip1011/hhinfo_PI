import globals
from time import sleep
import os
import sound as sound
from datetime import datetime

def autoUpdateTime():
    while True:
        prc=globals._RTC.timeUpdate
        if prc == 'fail' :
            sound.sysTimeUpdateFail()
            globals.initRTC()
        sleep(300)
