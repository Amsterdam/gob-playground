import time
import json
import threading

import pika


class AsyncConnection(object):

    def __init__(self, address, reconnect=False):
        self._connection = None
        self._channel = None
        self._eventloop = None

        self._address = address
        self._reconnect = reconnect
        self._on_connect_callback = None

        self._consumer_tags = []

    def _on_open_connection(self, connection):
        print("On open connection", connection)

        def on_close_channel(channel, code, text):
            print("On close channel", code, text)
            self._channel = None
            self._connection.close()


        def on_open_channel(channel):
            print("On open channel", channel)

            if self._on_connect_callback:
                self._on_connect_callback()

            self._lock.release()


        self._channel = connection.channel(on_open_callback=on_open_channel)
        self._channel.add_on_close_callback(on_close_channel)

    def connect(self, on_connect_callback=None):
        print("Open connection")

        def on_error_connection(connection, text):
            print("On error connection", text, connection)
            self.disconnect()


        def on_close_connection(connection, code, text):
            print("On close connection", code, text)
            self._connection = None


        self._on_connect_callback = on_connect_callback

        self._connection = pika.SelectConnection(
          pika.ConnectionParameters(self._address),
          on_open_callback=self._on_open_connection,
          on_open_error_callback=on_error_connection,
          on_close_callback=on_close_connection)

        self._lock = threading.Lock()
        self._lock.acquire()

        self._eventloop = threading.Thread(target = lambda: self._connection.ioloop.start())
        self._eventloop.start()

        self._lock.acquire()

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

    def subscribe(self, queues):
        def on_message(handler):

            def handle_message(channel, basic_deliver, properties, body):
                # Handle message
                if handler(body) is not False:
                    # Default is to acknowledge message
                    print("Ack")
                    # channel.basic_ack(basic_deliver.delivery_tag)

            return handle_message

        def on_queue_bind(handler, queue):
            consumer_tag = self._channel.basic_consume(on_message(handler), queue)
            self._consumer_tags.append(consumer_tag)
            return lambda frame: consumer_tag


        for queue in queues:
            self._channel.queue_bind(
                on_queue_bind(queue["handler"], queue["name"]),
                queue["name"],
                queue["name"],
                queue["key"]
            )

    def disconnect(self):
        print("Disconnect")

        def on_cancel_channel(frame):
            print("On cancel channel")
            if self._channel.is_open:
                print("Close channel")
                self._channel.close()


        if self._eventloop is not None:
            print("Cancelling")
            if len(self._consumer_tags):
                for consumer_tag in self._consumer_tags:
                    self._channel.basic_cancel(on_cancel_channel, consumer_tag)
            else:
                self._channel.close()
            self._eventloop.join()
            self._eventloop = None
            print("Eventloop has stopped")


        if self._connection is not None:
            self._connection.close()



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

connection = AsyncConnection('localhost')
connection.connect()
connection.subscribe(queues)
time.sleep(1)
connection.disconnect()
connection.disconnect()
print("End")
