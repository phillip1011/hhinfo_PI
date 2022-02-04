#!/bin/bash

#ping -c 1 -w 1 1.34.160.163  && result=0 || result=1
ping -c 1 -w 1 35.221.198.141 && result=0 || result=1

if [ "$result" -eq "0" ]; then

	echo "Server  is Online." 
	sudo  python3 /home/ubuntu/nfc/watchdog.py


else
	echo "can not find server ."
	aplay /home/ubuntu/nfc/mp3/Find_Server.wav
        sudo killall openvpn
        #sleep 60
       
fi




#sudo  python3 /home/ubuntu/nfc/watchdog.py 



#cd /home/ubuntu/nfc
#sudo python3 main.py > main.log 2>&1 &

