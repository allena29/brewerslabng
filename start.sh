#!/bin/sh

cd /home/beer/brewerslab/master/

date >/tmp/master_bootup
ping 192.168.1.10 &

mkdir ipc 2>/dev/null
mount -t tmpfs -o size=50M tmpfs ipc

/etc/init.d/rpcbind restart
/etc/init.d/nfs-kernel-server restart


chown beer /var/log/beer -R

rm -f simulator 2>/dev/null


# Set time/date
ntpdate -s uk.pool.ntp.org

rm ipc/*
date >ipc/handshake
date +%s >ipc/hlt-delay-until

#echo "modprobing gpio 1wire therm"
#modprobe w1-gpio
#modprobe w1-therm
echo "including i2c"
modprobe i2c-dev

mount -t tmpfs -o size=50m tmpfs /currentdata/

mkdir ipc/fermprogress
touch ipc/sparge-not-finished
touch ipc/ferm-notstarted
touch ipc/boil_getting-ready
touch ipc/mash_toggle_type-dough

# these should transition to screen type launhces
echo "Starting Flasher"
sh flasher.sh "Launching"
sh lcd.sh "Launching"
sh governor.sh "Lauching"
sh monitor.sh "Launching"
sh button.sh "Launching"

# Start  local server
sudo -u beer screen -dmS localweb python localweb/localserve.py

