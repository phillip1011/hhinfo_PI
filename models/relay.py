import RPi.GPIO as GPIO
import time
import threading

relaystatus = [0, 0, 0, 0]
LED_PIN = [5,6,13,16]
SEN_PIN = [17, 27, 22, 17, 27, 22]
HAND_PIN= [12,12]
relayaction = [0, 0, 0, 0]
GPIO.setmode(GPIO.BCM)

for i in range(4):
    GPIO.setup(LED_PIN[i], GPIO.OUT )
for i in range(6):
    GPIO.setup(SEN_PIN[i], GPIO.IN)
for i in range(2):
    GPIO.setup(HAND_PIN[i], GPIO.IN)

def setup():
    GPIO.setmode(GPIO.BCM)
    for i in range(4):
        GPIO.setup(LED_PIN[i], GPIO.OUT )
        GPIO.output(LED_PIN[i], 1)
    GPIO.setup(SEN_PIN, GPIO.IN)
    GPIO.setup(HAND_PIN,GPIO.IN)

def check_relay():
    for j in range(4):
        for i in range(4):
            GPIO.output(LED_PIN[i], 1)
        #time.sleep(1)
        GPIO.output(LED_PIN[j], 0)
        time.sleep(0.15)

def read_hand():
    xx = []
    for i in range(2):
        x = GPIO.input(HAND_PIN[i])
        #print(x, end="")
        xx.append(x)
    #print("")
    return xx

#[0,0,0,0,0,0]
#[[0,0],0,0,0,0,0]
def read_sensor():

    xx = []
    # xx = {

    # }
    for i in range(6):
        x = GPIO.input(SEN_PIN[i])
        #print(x, end="")
        if(x == 1):
            xx.append(0)
        else: 
            xx.append(1)
    #print("")
    return xx

def do_action(gateno,opentime,waittime):
    if (gateno == 0 ):
        return 
    gateno -= 1
    relayaction[gateno] = 1
    relay_pin = LED_PIN
    if waittime != 0 :
        time.sleep(waittime)
    if opentime == 0:
        GPIO.output(relay_pin[gateno], 1)
        # check 
        if(GPIO.input(relay_pin[gateno]) == 1):
            print("已關閉relay")
        else:
            print("關閉relay 失敗")
        relaystatus[gateno] = 0
    else:
        GPIO.output(relay_pin[gateno], 0)
        # check 
        if(GPIO.input(relay_pin[gateno]) == 0):
            print("已開啟relay")
        else:
            print("開啟relay 失敗")

        relaystatus[gateno] = 1
    if opentime < 255:
        time.sleep(opentime)
        GPIO.output(relay_pin[gateno], 1)
        relaystatus[gateno] = 0
    relayaction[gateno] =0

def action(gateno,opentime,waittime):
    t = threading.Thread(target=do_action, args=(gateno, opentime, waittime))
    t.start()



def cleanup():
    try:
        GPIO.cleanup()
    except:
        print("can not clean GPIO")

def start_relay():
    try:
        print("setup relay")
        setup()
        print("start check relay")
        x = 0
        while x < 5 :
            #print(i)
            x+=1
            #check_relay()

    except:
        print("relay error")
    finally:
        print("clean relay channel")
        for i in range(4):
            GPIO.output(LED_PIN[i], 1)
        #GPIO.cleanup()
        #action(1, 4, 0)
        #action(2, 4, 1)
        #action(3, 4, 2)
        #action(4, 4, 3)
    sen = read_sensor()

def command(comstring):
    this_serverip = comstring[0:comstring.find("&")]
    comstring=comstring[comstring.find("&")+1:]
    print(comstring)
    comms=comstring.split("&gate")
    print(comms)
    max_action_time = 0
    for comm in comms:
        commands = comm.split("&")
        values = []
        names = []
        for para in commands:
            xxx = para.split("=")
            names.append(xxx[0])
            xxx[1] = xxx[1].replace(' ', '')
            try:
                values.append(int(xxx[1]))
            except:
                values.append(0)
        if (len(values) < 3 ):
            values.append(0)
        if (len(values) < 3):
            values.append(0)
        action(values[0], values[1], values[2])
        if values[1] < 255 :
            action_time = values[1] +values[2]
        else :
            action_time = values[2]
        if action_time > max_action_time :
            max_action_time =action_time
        print(names)
        print(values)
    #time.sleep(action_time)
    rc = 0
    #for act in relayaction:
    #    if act ==1 :
    #        rc =1
    return rc


