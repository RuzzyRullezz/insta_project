import abc
import datetime

from django.utils import timezone


class IgLogCounter(metaclass=abc.ABCMeta):
    url_contains = NotImplemented

    def __init__(self, account, period=datetime.timedelta(hours=24), limit=float('inf')):
        self.account = account
        self.period = period
        self.limit = limit
        super().__init__()

    def get_ig_qset(self):
        from database.models import IgLog
        return IgLog.objects.filter(
            account=self.account,
            request_time__gte=timezone.now() - self.period,
            status_code=200,
        )

    def count(self):
        if self.url_contains is NotImplemented:
            raise NotImplementedError
        return self.get_ig_qset().filter(url__contains=self.url_contains).count()

    def get_available_requests_count(self):
        return self.limit - self.count()

    def inc(self):
        pass


class IgLogFollowingsCounter(IgLogCounter):
    url_contains = 'friendships/create'


class IgLogUnfollowingsCounter(IgLogCounter):
    url_contains = 'friendships/destroy'


class IgLogLikeCounter(IgLogCounter):
    url_contains = '/like/'


class IgLogLookingCounter(IgLogLikeCounter):
    url_contains = '/media/seen/'
