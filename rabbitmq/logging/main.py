import logging
import datetime
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()


class RequestsHandler(logging.Handler):
    def emit(self, record):

        # asctime 	%(asctime)s 	Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time).
        # created 	%(created)f 	Time when the LogRecord was created (as returned by time.time()).
        # filename 	%(filename)s 	Filename portion of pathname.
        # funcName 	%(funcName)s 	Name of function containing the logging call.
        # levelname	%(levelname)s 	Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        # levelno 	%(levelno)s 	Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        # lineno 	%(lineno)d 	    Source line number where the logging call was issued (if available).
        # module 	%(module)s 	    Module (name portion of filename).
        # msecs 	%(msecs)d 	    Millisecond portion of the time when the LogRecord was created.
        # message 	%(message)s 	The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
        # msg 	 	                The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Using arbitrary objects as messages).
        # name 	    %(name)s 	    Name of the logger used to log the call.
        # pathname 	%(pathname)s 	Full pathname of the source file where the logging call was issued (if available).
        # process 	%(process)d 	Process ID (if available).
        # processName 	    %(processName)s 	Process name (if available).

        log_msg = {
            "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.msg,
            "formatted_msg": self.format(record)
        }

        json_msg = json.dumps(log_msg)

        channel.basic_publish(
            exchange="gob.log",
            routing_key=record.levelname,
            properties=pika.BasicProperties(
                delivery_mode=2 # Make messages persistent
            ),
            body=json_msg
        )


def get_logger(name):
    format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    level = logging.DEBUG

    logger = logging.getLogger(name)

    logging.basicConfig(
        level=level,
        format=format
    )

    handler = RequestsHandler()
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = get_logger(__name__)
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')

metrics = {
    "name": "Import DIVA Gebieden",
    "id": "5d92018a-2403-4a4c-90e9-96a8d483ff59", # Use this also in logging
    "start_timestamp": "2018-06-28T14:37:15",
    "end_timestamp": "2018-06-28T14:38:16",
    "duration": 61.153, # in seconds
    "actions": [
        {
            "type": "ADD",
            "count": 30,
        },
        {
            "type": "MODIFIED",
            "count": 1,
        } # ,...
    ],
    "warnings": 0,
    "errors": 0,
    "result": 0
}
