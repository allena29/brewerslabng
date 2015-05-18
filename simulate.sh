#!/bin/sh
cd /home/allena29/piTempMonitor/master/


#mount -t tmpfs -o size=50m tmpfs ipc
mount | grep ipc | grep tmpfs &>/dev/null
if [ "$?" == "0" ]
then
echo -n ""
else
echo "mounting tmpfs"
sudo mount -t tmpfs -o size=50M tmpfs ipc
fi

sh killsimulate.sh

date >/tmp/master_bootup

touch simulator
rm ipc/*
date >ipc/handshake

touch ipc/boil_getting-ready
touch ipc/mash_toggle_type-dough

screen -dmS fakebutton python localweb/localserve.py
screen -dmS fakeheat python fakeheat.py



# these should transition to screen type launhces
sh flasher.sh "simulate"
sh lcd.sh "simulate"
sh governor.sh "simulate"
sh monitor.sh "simulate"
sh button.sh "simulate"


################### slave

date >/tmp/slave_bootup
cd /home/allena29/piTempMonitor/slave
touch simulator
mkdir "ipc/fake1wire" 2>/dev/null
mkdir "ipc/fake1wire/28-000003ebc866" 2>/dev/null
echo "91 01 4b 46 7f ff 0f 10 25 : crc=25 YES" >ipc/fake1wire/28-000003ebc866/w1_slave
echo "91 01 4b 46 7f ff 0f 10 25 : t=11000" >>ipc/fake1wire/28-000003ebc866/w1_slave
mkdir "ipc/fake1wire/28-000003eba86a" 2>/dev/null
echo "91 01 4b 46 7f ff 0f 10 25 : crc=25 YES" >ipc/fake1wire/28-000003eba86a/w1_slave
echo "91 01 4b 46 7f ff 0f 10 25 : t=67000" >>ipc/fake1wire/28-000003eba86a/w1_slave
mkdir "ipc/fake1wire/28-000003ebccea" r>/dev/null
echo "91 01 4b 46 7f ff 0f 10 25 : crc=25 YES" >ipc/fake1wire/28-000003ebccea/w1_slave
echo "91 01 4b 46 7f ff 0f 10 25 : t=67000" >>ipc/fake1wire/28-000003ebccea/w1_slave
mkdir "ipc/fake1wire/28-0000044dcda4" 2>/dev/null
echo "91 01 4b 46 7f ff 0f 10 25 : crc=25 YES" >ipc/fake1wire/28-0000044dcda4/w1_slave
echo "91 01 4b 46 7f ff 0f 10 25 : t=50000" >>ipc/fake1wire/28-0000044dcda4/w1_slave
mkdir "ipc/fake1wire/28-00044efeaaff" 2>/dev/null
echo "91 01 4b 46 7f ff 0f 10 25 : crc=25 YES" >ipc/fake1wire/28-00044efeaaff/w1_slave
echo "91 01 4b 46 7f ff 0f 10 25 : t=95000" >>ipc/fake1wire/28-00044efeaaff/w1_slave




sh temperature.sh "Launching"
sh ssr.sh "Launching"
sh relay.sh "Launching"
sh grapher.sh "Launching"
sh bidir.sh "Launching"





