import logging
import datetime
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.0.2'))
channel = connection.channel()


class RequestsHandler(logging.Handler):
    def emit(self, record):
        print(record)
        log_msg = {
            "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.msg,
            "formatted_msg": self.format(record)
        }
        # Send this log message as json object to log.levelname routing_key
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

