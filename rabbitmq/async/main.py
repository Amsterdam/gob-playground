import time
import json
import threading

import pika


class AsyncConnection(object):

    def __init__(self, address, queues, reconnect=False):
        self._connection = None
        self._channel = None

        self._address = address
        self._queues = queues
        self._reconnect = reconnect
        self._on_connect_callback = None


    def on_open_connection(self, connection):
        print("On open connection", connection)

        def on_close_channel(channel, code, text):
            print("On close channel", code, text)
            self.close_connection()


        def on_open_channel(channel):
            print("On open channel", channel)
            self._channel = channel

            def on_message(handler):

                def handle_message(channel, basic_deliver, properties, body):
                    # Handle message
                    if handler(body):
                        # On success, acknowledge message
                        print("Ack")
                        # channel.basic_ack(basic_deliver.delivery_tag)

                return handle_message

            def on_queue_bind(handler, queue):
                return lambda frame: channel.basic_consume(on_message(handler), queue)

            channel.add_on_close_callback(on_close_channel)

            for queue in self._queues:
                channel.queue_bind(
                    on_queue_bind(queue["handler"], queue["name"]),
                    queue["name"],
                    queue["name"],
                    queue["key"]
                )

            if self._on_connect_callback:
                self._on_connect_callback()

        connection.channel(on_open_callback=on_open_channel)

    def close_connection(self):
        self.disconnect()
        if self._reconnect:
            time.sleep(5)
            self.connect()


    def connect(self, on_connect_callback=None):
        print("Open connection")

        def on_error_connection(connection, text):
            print("On error connection", text, connection)
            self.close_connection()


        def on_close_connection(connection, code, text):
            print("On close connection", code, text)
            self.close_connection()

        self._on_connect_callback = on_connect_callback

        self._connection = pika.SelectConnection(
          pika.ConnectionParameters(self._address),
          on_open_callback=self.on_open_connection,
          on_open_error_callback=on_error_connection,
          on_close_callback=on_close_connection)


    def publish(self, queue, msg):
        if self._channel is None:
            raise Exception("Connection with message broker not available")

        json_msg = json.dumps(msg)

        self._channel.basic_publish(
            exchange=queue["name"],
            routing_key=queue["key"],
            properties=pika.BasicProperties(
                delivery_mode=2  # Make messages persistent
            ),
            body=json_msg
        )


    def subscribe(self):
        self._subscriber = threading.Thread(target = lambda: self._connection.ioloop.start())
        self._subscriber.start()


    def disconnect(self):
        self._connection.ioloop.add_callback_threadsafe(self._connection.ioloop.stop)

        if self._subscriber is not None:
            self._subscriber.join()
            self._subscriber = None

        self._connection.close()

        self._connection = None
        self._channel = None


def on_workflow(msg):
    print("Workflow", msg)
    return True


def on_log(msg):
    print("Log", msg)
    return True


queues = [
    {
        "name": "gob.workflow",
        "key": "#",
        "handler": on_workflow
    },
    {
        "name": "gob.log",
        "key": "#",
        "handler": on_log
    }
]

connection = AsyncConnection('localhost', queues)

def run():
    print("Run start")
    # connection.receive()
    connection.publish(queues[0], "Hello")
    print("Run end")
    time.sleep(5)
    connection.disconnect()

# atexit.register(connection.disconnect)

connection.connect()

connection.subscribe()

# subscriber = threading.Thread(target = lambda: connection.subscribe())
# subscriber.start()

time.sleep(2)
connection.publish(queues[0], "Hello")
time.sleep(1)

print("Disconnect")
connection.disconnect()

time.sleep(1)
print("End")
