import threading
import pytest
import pika

from .main import AsyncConnection

class MockIoloop:

    def __init__(self):
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        if not self.running:
            self.lock.acquire()
            self.running = True
            # Wait for stop() to have been called
            self.lock.acquire()
            self.running = False

    def stop(self):
        self.lock.release()

class MockChannel:

    connection_success = True

    consumer_callback = None
    consumer_tags = [1, 2, 3]
    on_close = None

    def add_on_close_callback(self, callback):
        self.on_close = callback
        if not self.connection_succes:
            callback(self, code=1, text="Error")

    def close(self):
        if self.on_close is not None:
            self.on_close(self, code=0, text="OnClose")

    def basic_publish(self,
                      exchange,
                      routing_key,
                      properties,
                      body):
        pass

    def basic_cancel(self,
                     callback,
                     consumer_tag):
        pass

    def queue_bind(self,
                   callback,
                   exchange,
                   queue,
                   routing_key):
        self.consumer_callback = callback
        callback({})

    def basic_consume(self,
                      consumer_callback,
                      queue):
        self.consumer_callback = consumer_callback
        consumer_callback(self, {}, {}, "body")

class MockConnection:

    connection_success = True

    on_close = None

    def __init__(self):
        self.ioloop = MockIoloop()

    def channel(self, on_open_callback):
        channel = MockChannel()
        channel.connection_succes = self.connection_success
        if self.connection_succes:
            on_open_callback(channel)
        return channel

    def close(self):
        if self.ioloop.running:
            self.ioloop.stop()
        if self.on_close is not None:
            self.on_close(self, code=0, text="OnClose")

    def __exit__(self):
        if self.ioloop.running:
            self.ioloop.stop()
        pass

class MockPika:

    selectConnectionOK = True

    def SelectConnection(self,
            parameters,
            on_open_callback,
            on_open_error_callback,
            on_close_callback):
        if self.selectConnectionOK:
            connection = MockConnection()
            connection.connection_succes = True
            connection.on_close = on_close_callback
            on_open_callback(connection)
            return connection
        else:
            on_open_error_callback(None, 'Fail to open connection')
            return None

def mock_connection(monkeypatch, connection_success):
    _pika = MockPika()
    _pika.selectConnectionOK = connection_success
    monkeypatch.setattr(pika, 'SelectConnection', _pika.SelectConnection)


is_on_connect_called = False

def get_on_connect():

    def on_connect():
        # Helper function to test callback on connect
        global is_on_connect_called
        is_on_connect_called = True


    # Helper function to test callback on connect
    global is_on_connect_called
    is_on_connect_called = False
    return on_connect


def test_connection_constructor():
    # Test if a connection can be initialized
    connection = AsyncConnection('address')
    assert(connection is not None)
    assert(connection._address == 'address')


def test_disconnect():
    # Test if a disconnect can be called without an earlier connect
    connection = AsyncConnection('')
    assert(connection.disconnect() is None)


def test_idempotent_disconnect():
    # Test disconnect repeated execution
    connection = AsyncConnection('')
    assert(connection.disconnect() is None)
    assert(connection.disconnect() is None)


def test_connect_failure(monkeypatch):
    # Test if connect reports failure to connect
    mock_connection(monkeypatch, connection_success=False)

    connection = AsyncConnection('address')
    assert(connection.connect() == False)


def test_connect_success(monkeypatch):
    # Test if connect reports connection success
    mock_connection(monkeypatch, connection_success=True)

    connection = AsyncConnection('address')
    assert(connection.connect() == True)
    connection.disconnect()


def test_connect_callback(monkeypatch):
    # Test if connect calls callback on success
    mock_connection(monkeypatch, connection_success=True)

    connection = AsyncConnection('address')
    connection.connect(get_on_connect())
    assert(is_on_connect_called)
    connection.disconnect()


def test_connect_callback(monkeypatch):
    # Test if connect does not call callback on failure
    mock_connection(monkeypatch, connection_success=False)

    connection = AsyncConnection('address')
    connection.connect(get_on_connect())
    assert(not is_on_connect_called)
    connection.disconnect()


def test_publish(monkeypatch):
    # Test publish message
    mock_connection(monkeypatch, connection_success=True)

    connection = AsyncConnection('address')
    connection.connect()
    queue = {
        "name": "name",
        "key": "key"
    }
    connection.publish(queue, "message")
    connection.disconnect()


def test_publish_failure(monkeypatch):
    # Test publish failure
    mock_connection(monkeypatch, connection_success=True)

    connection = AsyncConnection('address')
    queue = {
        "name": "name",
        "key": "key"
    }
    with pytest.raises(Exception):
        connection.publish(queue, "message")


def test_subscribe(monkeypatch):
    # Test subscription and message receipt
    mock_connection(monkeypatch, connection_success=True)

    result = None

    def on_message(body):
        assert(body == "body")

    connection = AsyncConnection('address')
    connection.connect()
    queue = {
        "name": "name",
        "key": "key",
        "handler": on_message
    }
    connection.subscribe([queue, queue])
    connection.disconnect()
