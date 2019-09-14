#!/usr/bin/env python
import pika
import sys
import time

credentials = pika.PlainCredentials('beerng', 'beerng')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.28', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World! %s" % (time.ctime())
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)
connection.close()
