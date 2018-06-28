import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()

exchange = channel.exchange_declare(
    exchange="gob.topic",
    exchange_type="topic",
    durable=True
)

exchange = channel.exchange_declare(
    exchange="gob.log",
    exchange_type="topic",
    durable=True
)

channel.queue_declare(
    queue="gob.topic",
    durable=True
)

channel.queue_declare(
    queue="gob.log",
    durable=True
)

channel.queue_bind(
    queue="gob.topic",
    exchange="gob.topic",
    routing_key="#"
)

channel.queue_bind(
    queue="gob.log",
    exchange="gob.log",
    routing_key="#"
)

def publish():
    channel.basic_publish(
        exchange="gob.topic",
        routing_key="fullupdate.proposal",
        properties=pika.BasicProperties(
            delivery_mode=2 # Make messages persistent
        ),
        body="Started"
    )

def on_receive(ch, method, properties, body):
    print(f"Received {body}")
    print("Do something")
    channel.basic_ack(delivery_tag=method.delivery_tag)

def try_receive():
    method, properties, body = channel.basic_get(
        queue='gob.topic'
    )
    if not method is None:
        on_receive(None, method, properties, body)

def receive():
    channel.basic_consume(
        consumer_callback=on_receive,
        queue='gob.topic'
    )

    channel.start_consuming()

connection.close()
