import json
import models.relay as relay


def openr3r4(authority):
    authority = authority.replace(' ','')
    print(authority)
    if (authority=='3'):
        relay.action(3,255,0)
    if (authority=='4'):
        relay.action(4,255,0)
    if (authority=='3,4'):
        relay.action(3,255,0)
        relay.action(4,255,0)


def opendoor(authority,doorstatus):
    print (authority,doorstatus)
    text_file = open("/home/ubuntu/nfc/DeviceData.txt", "r")
    datas = text_file.read()
    text_file.close()
    jData = json.loads(datas)
    if jData[0]["type"] == "鐵捲門" :
        if doorstatus == 1 :
            relay.action(1,1,0)
            openr3r4(authority)
        else:
            relay.action(2, 1, 0)
    else :
        relay.action(1, 4, 0)
        openr3r4(authority)


def checkdoor(uid):
    text_file = open("/home/ubuntu/nfc/vipcard.txt", "r")
    datas = text_file.read()
    text_file.close()
    print(datas)
    jDatas = json.loads(datas)
    for value in jDatas :
        if (value["card_uuid"] == uid ):
            print (uid)
            doorstatus = relay.read_sensor()[0]

            opendoor(value["authority"],doorstatus)


#if __name__ == '__main__':
#    checkdoor("3729863200")
