import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()
channel.queue_declare(queue='main')

while True:
    channel.basic_publish(exchange='',
                          routing_key='main',
                          body='Hello World!')
    print("Send")
    time.sleep(5)

connection.close()