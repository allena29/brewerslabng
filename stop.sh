#!/bin/bash

sh bidir.sh "kill"
sh ssr.sh "kill"
sh temperature.sh "kill"
sh grapher.sh "kill"
sh relay.sh "kill"


sync

cp /currentdata/* /archivedata/
sync


python relay-kill.py

if [ "$1" = "reboot" ]
then
/sbin/reboot
fi

if [ "$1" = "poweroff" ]
then
/sbin/poweroff
fi

