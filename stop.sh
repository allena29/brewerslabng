#!/bin/sh

echo "Stopping "
kill `ps -ef | grep "lighttpd -f lighttpd/brewerslab.conf" | grep -v "grep" | sed -e 's/^beer *//' | sed -e 's/ .*//' `

exit 0
