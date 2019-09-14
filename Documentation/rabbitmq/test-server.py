#!/usr/bin/env python
import json
import pika
import time
credentials = pika.PlainCredentials('beerng', 'beerng')


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.28', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

severity = 'aaa'
for c in range(500):
    message = 'abc' + str(c) + time.ctime()
    channel.basic_publish(
        exchange='direct_logs', routing_key=severity, body=message)
    print(" [x] Sent %r:%r" % (severity, message))
    time.sleep(1)
connection.close()
