#!/bin/sh
cd /home/pi/brewerslab/master/
date >/tmp/master_bootup
ping 192.168.1.10 &

rm -f simulator 2>/dev/null


# Set time/date
ntpdate -s uk.pool.ntp.org

rm ipc/*
date >ipc/handshake

#echo "modprobing gpio 1wire therm"
#modprobe w1-gpio
#modprobe w1-therm
echo "including i2c"
modprobe i2c-dev

mount -t tmpfs -o size=50m tmpfs /currentdata/


touch ipc/mash_toggle_type-dough

# these should transition to screen type launhces
echo "Starting Flasher"
sh flasher.sh "Launching"
sh lcd.sh "Launching"
sh governor.sh "Lauching"
sh monitor.sh "Launching"
sh button.sh "Launching"
