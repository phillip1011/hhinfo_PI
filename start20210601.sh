#!/bin/bash

ServerXY="true"
echo -n "waiting for VPN Server ..."

while("$ServerXY" -eq "true")
do 
	#ping -c 1 -w 1 1.34.160.163  && result=0 || result=1
	ping -c 1 -w 1 35.221.198.141 && result=0 || result=1

	if [ "$result" -eq "0" ]; then

        	echo "Server  is Online." 
		ServerXY="false"

	else

        	echo "."
		aplay /home/ubuntu/nfc/mp3/Find_Server.wav
                echo "ping server fail"
                sudo killall openvpn
                sleep 60
                #echo "sleep 60"
                #((i=i+1))
                #sudo reboot -h now
                ServerXY="false"

       
	fi
done




sudo  python3 /home/ubuntu/nfc/watchdog.py 



#cd /home/ubuntu/nfc
#sudo python3 main.py > main.log 2>&1 &

