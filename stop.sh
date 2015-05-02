#!/bin/bash

sh bidir.sh "kill"
sh ssr.sh "kill"
sh temperature.sh "kill"
sh grapher.sh "kill"
sh relay.sh "kill"

exit

sync

cp /currentdata/* /archivedata/
sync

if [ "$1" = "reboot" ]
then
sudo /sbin/reboot
fi

if [ "$1" = "poweroff" ]
then
sudo /sbin/poweroff
fi

