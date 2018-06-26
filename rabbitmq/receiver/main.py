import pika
import time

def callback(ch, method, properties, body):
    print(f"Received {body}")

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()
channel.queue_declare(queue='main')

channel.basic_consume(callback,
                      queue='main',
                      no_ack=True)
channel.start_consuming()

connection.close()
