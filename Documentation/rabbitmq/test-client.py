
import pika
credentials = pika.PlainCredentials('beerng', 'beerng')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.28', credentials=credentials))
channel = connection.channel()


channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
print('qn:', queue_name)

severity = 'aaa'
channel.queue_bind(
    exchange='direct_logs', queue=queue_name, routing_key=severity)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
