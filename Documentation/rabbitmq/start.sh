#!/bin/sh

/etc/init.d/rabbitmq-server start
rabbitmqctl add_user beerng beerng
rabbitmqctl set_user_tags beerng administrator
rabbitmqctl set_permissions -p / beerng ".*" ".*" ".*"


while true; do
sleep 10
done
