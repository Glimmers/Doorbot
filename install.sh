#!/bin/sh

if [ "$USER" != "root" ]
then
     echo "This installer must be run with root privileges. Please run sudo $0"
     return 1
fi

# Ensure the libraries we use are installed
apt install python3 python3-rpi.gpio python3-requests

addgroup --system doorbot
adduser --system --ingroup gpio doorbot

for N in doorbot.ini.example doorbot.py doorbot.service ringtest.py
    do cp $N /home/doorbot
    chown doorbot:doorbot /home/doorbot/$N
done

if [ -f /etc/systemd/system/doorbot.service ]
    then echo "Unit file already exists, skipping"
    else ln /home/doorbot/doorbot.service /etc/systemd/system/
fi
systemctl daemon-reload

