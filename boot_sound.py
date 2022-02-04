import os
from time import sleep



os.system("aplay /home/ubuntu/nfc/mp3/boot.wav")
os.system("aplay /home/ubuntu/nfc/mp3/Wait3min.wav")
sleep(30)
os.system("aplay /home/ubuntu/nfc/mp3/Wait0.wav")
sleep(30)
os.system("aplay /home/ubuntu/nfc/mp3/Wait1.wav")
sleep(30)
os.system("aplay /home/ubuntu/nfc/mp3/Wait2.wav")
sleep(30)
os.system("aplay /home/ubuntu/nfc/mp3/Wait3.wav")

