import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()
channel.queue_declare(queue='gob.workflow', durable=True)

while True:
    channel.basic_publish(exchange='gob.workflow',
                          routing_key='test',
                          body='Hello World!',
                          properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                          ))
    print("Send")
    time.sleep(5)

connection.close()
