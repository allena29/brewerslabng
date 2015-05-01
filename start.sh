#!/bin/sh
cd /home/allena29/piTempMonitor/master/
date >/tmp/master_bootup
ping 192.168.1.10 &

rm -f simulator 2>/dev/null
#replaced with a bridge
#echo "Enabling NAT for our slaves"
#echo "1" >/proc/sys/net/ipv4/ip_forward
#/sbin/iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
#/sbin/iptables -A FORWARD -i wlan0 -o eth1 -m state   --state RELATED,ESTABLISHED -j ACCEPT
#/sbin/iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT


# Disable IGMP Snoopin
#echo 0 > /sys/devices/virtual/net/br0/bridge/multicast_snooping 
# Set Bridge MAC-Address to something the homehub likes
#/sbin/ifconfig br0 hw ether b8:27:eb:75:de:ad


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
sh monitor.sh "Launchin"
sh button.sh "Launching"
