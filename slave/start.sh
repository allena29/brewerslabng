#!/bin/sh

sleep 55

date >/tmp/slave_bootup
ping 192.168.1.13 >/dev/null 2>/dev/null  &


echo "Remove old flags each reboot"
rm -f /home/beer/brewerslab/slave/localweb/wifistate/*

if [ -F "/features/diabled/local-wifi-ap" ]
then
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
fi 



/etc/init.d/rpcbind restart

cd /home/beer/brewerslab/slave
mkdir ipc 2>/dev/null

mkdir ipc/fermprogress
touch ipc/sparge-not-finished
touch ipc/ferm-notstarted
touch ipc/boil_getting-ready
touch ipc/mash_toggle_type-dough
touch ipc/whirlpool-not-started

mount -t tmpfs -o size=50M tmpfs ipc


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
mkdir /currentdata/lastreading


###################################
### LOCAL ENVIRONMENT
echo "Mount NAS "
mount -t nfs -o nolock 192.168.1.31:/Transient/piTempMonitor/archivedata /archivedata
mount 192.168.1.31:/web /web
/etc/init.d/rpcbind restart
###################################

if [ -f features/disabled/pitm-slave ]
then
	echo "PTIM SLAVE DISABLED"
else
	sh temperature.sh "Launching"
	sh ssr.sh "Launching"
	sh relay.sh "Launching"
	sh grapher.sh "Launching"
	sh bidir.sh "Launching"
fi

if [ -f features/disabled/led-matrix ]
then
	echo "lED MATRIX DISABLED"
else
	ip=`ifconfig wlan0 | grep Bcast | sed -e 's/.*ddr://' | sed -e 's/ .*//'`
	sudo python /home/beer/brewerslab/ledmatrix.py "ready.. http://$ip:54661/cgi/index.py"
	sudo sh summary.sh "Launchin"
fi


if [ -f "/boot/pitmautostart.txt" ]
then
	sh /home/beer/brewerslab/slave/launch-standalone-temp.sh
fi


screen -dmS localweb python localweb/localserve.py

if [ -f features/disabled/elasticsearch ]
then
	echo "ELASTICSEARCH DISABLED"
else
	cd /home/beer/elasticsearch-6.0.0
	screen -dmS elastic sudo -u beer ES_JAVA_OPTS="-Xms512m -Xmx512m" bin/elasticsearch 
	screen -dmS elastic-sub sh elastic.sh
fi

