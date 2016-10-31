


if [ -f /tmp/standalone-temp-active ]
then

 echo "alreay doing temp"
else

	touch /tmp/standalone-temp-active
	cd /home/beer/brewerslab/slave

	echo "nameserver 8.8.8.8" >/etc/resolv.conf
	sleep 2
	ntpdate -s uk.pool.ntp.org





	echo "start grapher"

	cd /home/beer/brewerslab/slave
	sh grapher.sh "Launching" 
	sleep 4
	sh ledmatrix.sh "Launchin"
	sh temperature.sh "Launching"

	python pitmLedMatrix.py "Temperature Monitor Started"

	cd /home/beer/brewerslab/master/
	touch /tmp/led-matrix-monitor
fi
	exit 0
