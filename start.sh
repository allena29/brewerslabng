#!/bin/sh

date >/tmp/slave_bootup
ping 192.168.1.10 &
mount 192.168.1.31:/web /web

/etc/init.d/rpcbind restart

cd /home/beer/brewerslab/slave
mkdir ipc 2>/dev/null


echo "including i2c"
modprobe i2c-dev
modprobe w1-gpio
modprobe w1-therm



ntpdate -s uk.pool.ntp.org

echo "Mount Tmpfs"
mount -t tmpfs -o size=50m tmpfs /currentdata

echo "Mount NAS "
mount -t nfs -o nolock 192.168.1.31:/Transient/piTempMonitor/archivedata /archivedata

/etc/init.d/rpcbind restart

sh temperature.sh "Launching"
sh ssr.sh "Launching"
sh relay.sh "Launching"
sh grapher.sh "Launching"
sh bidir.sh "Launching"




