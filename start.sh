#!/bin/sh

cd /home/beer/brewerslab/commander/

mkdir lighttpd/cache 2>/dev/null
mkdir metroui/progress  2>/dev/null
chown beer:beer lighttpd/cache
echo "Starting "

lighttpd -f lighttpd/brewerslab.conf

cd websocket
screen -dmS websocket python server.py


exit 0
