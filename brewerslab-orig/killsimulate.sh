#!/bin/bash

sh flasher.sh "kill"
sh monitor.sh "kill"
sh button.sh "kill"
sh lcd.sh "kill"
sh governor.sh "kill"
cd ../"slave"
sh temperature.sh "kill"
sh ssr.sh "kill"
sh grapher.sh "kill"
sh relay.sh "kill"
sh bidir.sh "Kill"

kill `ps -ef | grep "python localweb/localserve.py" | grep -v SCREEN | grep -v grep | sed -e 's/[a-z0-9]*\s*//' -e 's/\s.*//'` 2>/dev/null
kill `ps -ef | grep "python fakeheat.py" | grep -v SCREEN | grep -v grep | sed -e 's/[a-z0-9]*\s*//' -e 's/\s.*//'` 2>/dev/null
