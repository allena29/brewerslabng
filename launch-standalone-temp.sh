


if [ -f /tmp/standalone-temp-active ]
then

 echo "alreay doing temp"
else

	touch /tmp/standalone-temp-active



	echo "Kill Inidictor we can take care of that ourself"
	kill `ps -ef | grep gpio23led | head -n 1 | sed -e 's/^\S* *//' | sed -e 's/ .*//'`


	echo "nameserver 8.8.8.8" >/etc/resolv.conf
	ntpdate -s uk.pool.ntp.org


	python /home/beer/brewerslab/gpio23led.py 4 &



	echo "start grapher"

	cd /home/beer/brewerslab/slave
	sh grapher.sh "Launching" 
	sleep 4

	sh temperature.sh "Launching"
fi
	exit 0
