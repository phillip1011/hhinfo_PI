#!/bin/bash
sudo cp systemctl_config/hhinfo_boot.service /lib/systemd/system/hhinfo_boot.service
sudo cp systemctl_config/hhinfo_main.service /lib/systemd/system/hhinfo_main.service
sudo cp systemctl_config/rc.local /etc/rc.local
sudo systemctl daemon-reload
sudo systemctl enable hhinfo_boot
sudo systemctl enable hhinfo_main
#sudo systemctl enable rc-local.service
cp example_config.ini config.ini