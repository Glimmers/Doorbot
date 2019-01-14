#!/bin/sh

if [ "$USER" != "root" ]
then
     echo "This installer must be run with root privileges. Please run sudo $0"
     return 1
fi

# Ensure the libraries we use are installed
apt install python3-rpi.gpio python3-requests

addgroup --system doorbot
adduser --system --ingroup gpio doorbot
cp doorbot.ini.example doorbot.py doorbot.service ringtest.py /home/doorbot
ln /home/doorbot/doorbot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable doorbot.service

