import datetime
import time

from django.utils import timezone
from counters.redis_counter import RedisCounter, TimeCounter


class CounterCleaner(RedisCounter):
    def __init__(self, save_period=datetime.timedelta(days=3)):
        super().__init__()
        self.save_period = save_period
        self.namespace = TimeCounter.namespace

    def get_namespace_keys(self):
        for key in self.client.scan_iter(f"{self.namespace}:*"):
            yield key

    def clean(self):
        for key in self.get_namespace_keys():
            score_max = time.mktime((timezone.now() - self.save_period).timetuple())
            self.remove(key, float('-inf'), score_max)
