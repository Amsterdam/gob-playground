import time
import json
import threading

import pika


def progress(*args):
    print("Progress", *args)


class AsyncConnection(object):
    """This is an asynchronous RabbitMQ connection.

    It handles unexpected conditions when interacting with RabbitMQ

    Threading and locks are used to provide for a synchronous connection setup and
    to allow both publishing and subscribing in parallel.

    The connection allows for an unlimited number of subscriptions.

    Extensive use of closures is made to handle the asynchronous communication with RabbitMQ

    No automatic reconnection with RabbitMQ is implemented.

    """

    def __init__(self, address):
        """Create a new AsyncConnection

        :param address: The RabbitMQ address
        """

        # The address of the RabbitMQ Message broker
        self._address = address

        # The Connection and Channel objects
        self._connection = None
        self._channel = None

        # The RabbitMQ eventloop thread
        self._eventloop = None

        # Optional method, called on connection established
        self._on_connect_callback = None

    def _on_open_connection(self, connection):
        """Called on successful connection to RabbitMQ

        A channel will be created for the communication with RabbitMQ

        :param connection: The connection that has been establishe
        :return: None
        """

        # Register the connection
        self._connection = connection

        def on_close_channel(channel, code, text):
            """Called when a channel is closed

            :param channel: The channel that is closed
            :param code: The code for the channel closure
            :param text: The test for the channel closure
            :return: None
            """

            progress("Channel closed:", code, text)
            # self._channel = None
            # Close the connection
            self._connection.close()


        def on_open_channel(channel):
            """Called when a channel has been successfully established

            :param channel: The Channel object
            :return: None
            """

            # If a callback has been defined for connection success, call this function
            if self._on_connect_callback:
                self._on_connect_callback()
                # Call it only once
                self._on_connect_callback = None

            # Release the lock set in the connect() function so that this function can return the result
            self._lock.release()


        # Create a Channel, on_open_channel is called on success
        self._channel = connection.channel(on_open_callback=on_open_channel)

        # Register a function to handle the closure of the channel
        self._channel.add_on_close_callback(callback=on_close_channel)

    def connect(self, on_connect_callback=None):
        """Connect to RabbitMQ.

        :param on_connect_callback: This function will be called when a connection has been established
        :return bool: True when the connection has been established, False otherwise
        """

        def on_error_connection(connection, text):
            """This function is called on a connection error

            The lock that has been set on connection creation will be released.
            The connect function will be released and notice that no channel has been created.
            It will therefore return False to inform the caller that no connection could be established

            The disconnect method will be called to clean up the connection properties and stop the eventloop.

            :param connection: The connection object
            :param text: The error text
            :return: None
            """

            progress("Connection error:", text)
            self._lock.release()
            self.disconnect()


        def on_close_connection(connection, code, text):
            """Called when a connection is closed

            :param connection: The RabbitMQ connection object
            :param code: The error code
            :param text: The error text
            :return: None
            """

            progress("Connection closed:", code, text)
            # self._connection = None


        def eventloop():
            """The RabbitMQ eventloop.

            An ioloop is started to listen for messages for the active subscriptions.

            :return: None
            """
            try:
                self._connection.ioloop.start()
            except Exception as e:
                progress("Eventloop exception:", e)


        # A callback function can be specified that will be called when a connection is established
        self._on_connect_callback = on_connect_callback

        # Obtain a lock. The lock will be release on connection establishment or on failure
        self._lock = threading.Lock()
        self._lock.acquire()

        # Create a connection object
        self._connection = pika.SelectConnection(
          parameters=pika.ConnectionParameters(self._address),
          on_open_callback=self._on_open_connection,
          on_open_error_callback=on_error_connection,
          on_close_callback=on_close_connection)

        # Start the RabbitMQ eventloop
        self._eventloop = threading.Thread(target=eventloop)
        self._eventloop.start()

        # Wait for the lock to be released to be able to report success or failure
        self._lock.acquire()

        # Check whether a channel has been created, which means the connection has been established
        return self._channel is not None

    def publish(self, queue, key, msg):
        """Publish a message on a queue

        The message will be converted to json before publishing it on the queue

        :param queue: The queue object
        :param msg: The message
        :return: None
        """

        # Check whether a connection has been established
        if self._channel is None:
            raise Exception("Connection with message broker not available")

        # Convert the message to json
        json_msg = json.dumps(msg)

        # Publish the message as a persistent message on the queue
        self._channel.basic_publish(
            exchange=queue["name"],
            routing_key=key,
            properties=pika.BasicProperties(
                delivery_mode=2  # Make messages persistent
            ),
            body=json_msg
        )

    def subscribe(self, queues, message_handler):
        """Subscribe to the given queues

        :param queues: The queues to subscribe on
        :return: None
        """

        def on_message(queue):
            """This function is called for every message that is received

            The specified handler will be called to let the application handle the message.
            Default behaviour is to acknowledge the message after it has been successfully handled.
            If the handler returns False the message will not be acknowledged and stay on the queue

            :param handler: The user specified handler function
            :return: The handle message function
            """

            def handle_message(channel, basic_deliver, properties, body):
                """Handle the incoming message

                The message body is a json object which will be parsed on receipt (todo)

                Call the handler and acknowledge the message after it has been successfully handled

                :param channel: todo
                :param basic_deliver: todo
                :param properties: todo
                :param body: The message body
                :return:
                """

                # Try to parse body as json message, else pass it as it is received
                msg = body
                try:
                    msg = json.loads(body)
                except json.decoder.JSONDecodeError:
                    pass

                if message_handler(queue["name"], basic_deliver.routing_key, msg) is not False:
                    # Default is to acknowledge message
                    channel.basic_ack(basic_deliver.delivery_tag)

            return handle_message

        def on_queue_bind(queue):
            """Calles on successfully bind to the given queue

            A consumer will be created to consume the messages from the queue

            :param handler: The handler to call when a message is received
            :param queue: The name of the queue
            :return: A method that links the handler to a consumer
            """
            return lambda frame: self._channel.basic_consume(
                consumer_callback=on_message(queue),
                queue=queue["name"])

        # Subscribe to each queue in the list
        for queue in queues:
            self._channel.queue_bind(
                callback=on_queue_bind(queue),
                exchange=queue["name"],
                queue=queue["name"],
                routing_key=queue["key"]
            )

    def disconnect(self):
        """Disconnect from RabbitMQ

        Stop any running eventloop
        Close any open channels
        Close the connection

        :return: None
        """

        # Close any open channel
        if self._channel is not None and self._channel.is_open:
            # Cancel consumers
            for consumer_tag in self._channel.consumer_tags:
                self._channel.basic_cancel(
                    callback=lambda frame: None,
                    consumer_tag=consumer_tag)
            self._channel.close()
        self._channel = None

        # Close any running eventloop
        if self._eventloop is not None:
            try:
                self._eventloop.join()
            except RuntimeError:
                # The eventloop is already closing
                pass
        self._eventloop = None

        # Close any open connection
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
        self._connection = None


def on_message(queue, key, msg):
    print("Workflow", queue, key, msg)
    return True


queues = [
    {
        "name": "gob.workflow",
        "key": "#"
    },
    {
        "name": "gob.log",
        "key": "#"
    }
]

connection = AsyncConnection('localhost')
if connection.connect():
    connection.subscribe(queues, on_message)
    connection.publish(queues[1], "mykey", {"message": "Hello"})
    time.sleep(1)
    connection.disconnect()
    connection.disconnect()
