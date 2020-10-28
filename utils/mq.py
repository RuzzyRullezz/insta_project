import pika

from django.conf import settings
from mq_consumer.connectors import Connector


def get_connector(queue,
                  exchange=settings.RMQ_EXCHANGE_DEFAULT,
                  exchange_type=settings.RMQ_EXCHANGE_DEFAULT_TYPE,
                  routing_key=None):
    connection_parameters = pika.ConnectionParameters(
        host=settings.RMQ_HOST,
        port=settings.RMQ_PORT,
        credentials=pika.credentials.PlainCredentials(settings.RMQ_USER, settings.RMQ_PASSWORD),
        heartbeat_interval=0,
        connection_attempts=1,
    )
    return Connector(
        connection_parameters,
        exchange,
        queue,
        exchange_type=exchange_type,
        routing_key=routing_key,
    )
