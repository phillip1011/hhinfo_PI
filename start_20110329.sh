#!/bin/bash

ServerXY="true"
echo -n "waiting for VPN Server ..."

while("$ServerXY" -eq "true")
do 
	ping -c 1 -w 1 1.34.160.163  && result=0 || result=1

	if [ "$result" -eq "0" ]; then

        	echo "Server  is Online." 
		ServerXY="false"

	else

        	echo "."
       
	fi
done



ping -c 1 -w 1 10.0.0.1  && result=0 || result=1

if [ "$result" -eq "0" ]; then
        echo "VPN is connect."
        sudo  python3 /home/ubuntu/nfc/watchdog.py 
else
        echo "Connect to VPN."
	sudo pon pptpd
	#sudo pptpsetup --create hhinfo1 --server 1.34.160.163 --username hhinfo1 --password 12345678 --encrypt --start
fi



#cd /home/ubuntu/nfc
#sudo python3 main.py > main.log 2>&1 &

