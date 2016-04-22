#!/bin/sh

date >/tmp/slave_bootup

echo "Remove old flags each reboot"
rm -f /home/beer/brewerslab/slave/localweb/wifistate/*






/etc/init.d/rpcbind restart


echo "Starting Local WIFI"
sh /home/beer/brewerslab/start-local-wifi-hotspot.sh


if [ -f /home/beer/brewerslab/localweb/wifistate/.__GLOBAL__ ]
then

echo "Delay switched to configure SSID"

 sh /home/beer/brewerslab/replace-local-wifi-hotspot.sh     &

fi

 

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

echo "Starting Local Server"
su - beer -c "/usr/bin/screen -dmS localweb python localweb/localserve.py"


