#!/bin/bash


echo "stopping governor/probe/"
sh monitor.sh "kill"
sh governor.sh "kill"
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

