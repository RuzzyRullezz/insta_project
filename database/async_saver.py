import json

from django.db import IntegrityError
from mq_consumer.consumers import Consumer

from utils.mq import get_connector


class DBSaver(Consumer):
    def __init__(self):
        from database import models
        queue = 'db_save'
        self.model_attr = 'model'
        self.models = models
        super().__init__(get_connector(queue), self.handle)

    def handle(self, channel, method, properties, body):
        data = json.loads(body)
        model = data.pop(self.model_attr)
        model_cls = getattr(self.models, model)
        obj = model_cls(**data)
        try:
            obj.save()
        except IntegrityError:
            pass
        channel.basic_ack(delivery_tag=method.delivery_tag)
