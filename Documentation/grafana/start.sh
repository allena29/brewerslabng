#!/bin/bash

/etc/init.d/grafana-server start || echo 'Overlook error - it always givens an unclean exit sttus'
/etc/init.d/influxdb restart

while true; do
sleep 10
done

