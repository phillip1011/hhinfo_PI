import RPi.GPIO as GPIO
import threading
import pn532.pn532 as nfc
from pn532 import *
import time


def check_nfc():
    #pn532 = PN532_SPI(cs=4, reset=20, debug=False)
    pn532 = PN532_I2C(debug=False, reset=20, req=16)
    #pn532 = PN532_UART(debug=False, reset=20)

    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()
    print('Waiting for RFID/NFC card to read from!')
    GPIO.clean()
def do_read_mifare(blockno,t_callback = None):
    # pn532 = PN532_SPI(cs=4, reset=20, debug=False)
    pn532 = PN532_I2C(debug=False, reset=20, req=16)
    # pn532 = PN532_UART(debug=False, reset=20)
    pn532.SAM_configuration()
    while True:
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            # Try again if no card is available.
            if uid is not None:
                break
        print('Found card with UID:', [hex(i) for i in uid])
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        i = blockno
        try:
            pn532.mifare_classic_authenticate_block(
                uid, block_number=i, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
            #print(i, ':', ' '.join(['%02X' % x
            #                        for x in pn532.mifare_classic_read_block(i)]))
            xx = pn532.mifare_classic_read_block(i)
            if (t_callback != None):
                t_callback(i, xx)
        except nfc.PN532Error as e:
            xx = []
            if (t_callback != None):
                t_callback(-1, xx)
            #print(e.errmsg)
        time.sleep(2)


