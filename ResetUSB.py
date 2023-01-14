import os
import sys
from subprocess import Popen, PIPE
import fcntl

def ResetUSB():
    driver ="HL-340"
    print("重啟USB:", driver)
    USBDEVFS_RESET= 21780
    lsusb_out = Popen("lsusb | grep -i %s"%driver, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().split()
    bus = str(lsusb_out[1])[2:5]
    device = str(lsusb_out[3])[2:5]
    f = open("/dev/bus/usb/%s/%s"%(bus, device), 'w', os.O_WRONLY)
    fcntl.ioctl(f, USBDEVFS_RESET, 0)

