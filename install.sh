#!/bin/bash

USER=oudeis
HOME=/home/$USER
APP_HOME=$HOME/pi-timelapse
SYSTEMD_HOME=/etc/systemd/system
MAIN_SERVICE=timelapse.service
USB_SERVICE=timelapse-usb.service

echo pi-timelapse install starting...

cd $HOME
echo Updating OS and installing system dependencies...
# sudo apt update

# USB
sudo apt -y install exfat-fuse

echo Downloading pi-timelapse...
curl -L https://github.com/oudeismetis/pi_timelapse/archive/main.zip > pi_timelapse-main.zip
unzip -q pi_timelapse-main.zip && mv pi_timelapse-main pi_timelapse 
rm pi_timelapse-main.zip
cd $APP_HOME

echo Installing Python dependencies...
pip3 install -r requirements.txt

echo installing $MAIN_SERVICE...
sudo cp $APP_HOME/scripts/$MAIN_SERVICE $SYSTEMD_HOME
sudo chmod 644 $SYSTEMD_HOME/$MAIN_SERVICE
sudo systemctl start $MAIN_SERVICE
sudo systemctl enable $MAIN_SERVICE

echo installing $USB_SERVICE...
sudo cp $APP_HOME/scripts/$USB_SERVICE $SYSTEMD_HOME
sudo chmod 644 $SYSTEMD_HOME/$USB_SERVICE
sudo systemctl start $USB_SERVICE
sudo systemctl enable $USB_SERVICE

sudo systemctl daemon-reload

# install crontab
chmod a+x $APP_HOME/scripts/timelapse-delete-files.sh
crontab -u $USER $APP_HOME/scripts/crontab-timelapse

echo *************************************
echo pi-timelapse install complete.
echo *************************************
echo *****Reboot to ensure all installed dependencies work as expected*****
