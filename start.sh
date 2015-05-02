#!/bin/sh

date >/tmp/slave_bootup
ping 192.168.1.10 &

mount 192.168.1.31:/web /web

cd /home/allena29/piTempMonitor/slave


echo "including i2c"
modprobe i2c-dev
modprobe w1-gpio
modprobe w1-therm



ntpdate -s uk.pool.ntp.org

echo "Mount Tmpfs"
mount -t tmpfs -o size=50m tmpfs /currentdata

echo "Mount NAS "
mount -t nfs -o nolock 192.168.1.31:/Transient/piTempMonitor/archivedata /archivedata

sh temperature.sh "Launching"
sh ssr.sh "Launching"
sh relay.sh "Launching"
sh grapher.sh "Launching"
sh bidir.sh "Launching"




