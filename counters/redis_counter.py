import time
import datetime

import redis
from django.utils import timezone
from django.conf import settings


class RedisCounter:
    def __init__(self):
        self.host = settings.REDIS['default']['HOST']
        self.port = settings.REDIS['default']['PORT']
        self.database = settings.REDIS['default']['DATABASE']
        self.client = self.create_connection()

    def create_connection(self):
        return redis.StrictRedis(host=self.host, port=self.port, db=self.database)

    def add(self, key, score, value):
        self.client.zadd(key, {value: score})

    def count(self, key, score_min, score_max):
        return self.client.zcount(key, score_min, score_max)

    def remove(self, key, score_min, score_max):
        self.client.zremrangebyscore(key, score_min, score_max)


class TimeCounter(RedisCounter):
    namespace = 'time_counter'

    def __init__(self, key, period=datetime.timedelta(hours=24), limit=float('inf')):
        self.key = f'{self.namespace}:{key}'
        self.period = period
        self.limit = limit
        super().__init__()

    @staticmethod
    def get_score():
        return int(time.time())

    def set(self, value):
        score = self.get_score()
        self.add(self.key, score, value)

    def inc(self):
        self.set(self.get_score())

    def get_scores_interval(self):
        end = timezone.now()
        begin = end - self.period
        return int(time.mktime(begin.timetuple())), int(time.mktime(end.timetuple()))

    def count(self):
        score_min, score_max = self.get_scores_interval()
        return super().count(self.key, score_min, score_max)

    def get_available_requests_count(self):
        return self.limit - self.count()
