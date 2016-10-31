#!/bin/sh

date >/tmp/slave_bootup

#echo "Remove old flags each reboot"
#rm -f /home/beer/brewerslab/slave/localweb/wifistate/*

/etc/init.d/rpcbind restart


if [ -f "/boot/wifipsk.txt" ]
then
	if [ -f "/boot/wifissid.txt" ]
	then
		wifi=1
	else
		wifi=0
	fi
else
	wifi=0
fi

if [ $wifi = 0 ]
then
	echo "Starting Local WIFI"
	sh /home/beer/brewerslab/start-local-wifi-hotspot.sh
	sleep 2
	route add default gw 172.12.12.1
else
	echo "Joining real WIFI"
	sh /home/beer/brewerslab/replace-local-wifi-hotspot.sh     
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



echo "Mount Tmpfs"
mount -t tmpfs -o size=50m tmpfs /currentdata
mkdir /currentdata/lastreading


echo "Starting Local Server"
sudo -u beer /usr/bin/screen -dmS localweb python localweb/localserve.py

ip=`ifconfig wlan0 | grep Bcast | sed -e 's/.*ddr://' | sed -e 's/ .*//'`
sudo python /home/beer/brewerslab/ledmatrix.py "ready.. http://$ip:54661/cgi/index.py"

cd /home/beer/brewerslab/slave
sh ledmatrix.sh "Launchin"

if [ -f "/boot/pitmautostart.txt" ]
then

sh /home/beer/brewerslab/slave/launch-standalone-temp.sh

fi

