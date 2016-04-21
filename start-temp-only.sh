#!/bin/sh

date >/tmp/slave_bootup
ping 192.168.1.10 &





/etc/init.d/rpcbind restart

cd /home/beer/brewerslab/slave
mkdir ipc 2>/dev/null


echo "including i2c"
modprobe i2c-dev
modprobe w1-gpio
modprobe w1-therm

chown /var/log/beer -R
mkdir /web
mkdir /currentdata
mkdir /archivedata
chown beer:beer /web
chown beer:beer /currentdata
chown beer:beer /archivedata


ntpdate -s uk.pool.ntp.org

echo "Mount Tmpfs"
mount -t tmpfs -o size=50m tmpfs /currentdata

sh temperature.sh "Launching"
sh grapher.sh "Launching"

screen -dmS localweb python localweb/localserve.py


