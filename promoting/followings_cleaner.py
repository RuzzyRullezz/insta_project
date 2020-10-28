import time

import requests
from django.utils import timezone
from django.utils.timezone import make_aware
from pyctogram.instagram_client.client import InstagramClient, InstagramNot2XX, InstagramNoneResponse
from pyctogram.instagram_client.logger import RequestLog
from pyctogram.instagram_client.web import get_user_info

from counters.redis_counter import TimeCounter
from database.models import Accounts, IgLog, Following


class FollowingsCleaner:
    def __init__(self, account: Accounts,  sleep_time=30, proxies=None):
        self.account = account
        self.ig_client = InstagramClient(account.username, account.password,
                                         proxies=proxies, log_func=self.log_request)
        self.logged = False
        self.account_ig_id = int(get_user_info(account.username)['pk'])
        self.request_max_attempts = 100
        self.sleep_time = sleep_time
        self.ig_request_counter = TimeCounter(f'{account.username}:unfollowing')

    def log_request(self, log_record: RequestLog):
        log_params = log_record.__dict__
        log_params.update({
            'request_time': make_aware(log_params.pop('request_timestamp')),
            'response_time': log_params.pop('response_timestamp'),
        })
        if log_params['response_time']:
            log_params['response_time'] = make_aware(log_params['response_time'])
        IgLog(account=self.account, **log_params).save()

    def unfollow(self, user_ig_id, close_status=Following.Unfollow.code):
        unfollow_attempts = 0
        while True:
            try:
                unfollow_attempts += 1
                self.ig_client.unfollow(user_ig_id)
                self.ig_request_counter.inc()
                Following.objects.filter(profile__instagram_id=user_ig_id, owner=self.account).update(
                    closed=timezone.now(),
                    status=close_status,
                )
                time.sleep(self.sleep_time)
                break
            except (requests.exceptions.RequestException, InstagramNot2XX) as exc:
                if isinstance(exc, requests.exceptions.RequestException) or isinstance(exc,
                                                                                       InstagramNoneResponse) or \
                        (isinstance(exc, InstagramNot2XX) and 500 <= exc.status_code <= 599):
                    if unfollow_attempts <= self.request_max_attempts:
                        time.sleep(float(unfollow_attempts) / 2)
                        continue
                    else:
                        raise
                else:
                    raise

    def cancel_all_followings(self):
        if not self.logged:
            self.ig_client.login()
            self.logged = True
        for users_list in self.ig_client.get_followings(self.account_ig_id):
            for followed_user in users_list:
                self.unfollow(int(followed_user['pk']), close_status=Following.Unfollow.code)
        for requested_user in self.ig_client.get_outgoing_requests():
            self.unfollow(int(requested_user['pk']), close_status=Following.Unrequested.code)

    def repair_db(self):
        Following.objects.filter(
            owner=self.account,
            closed__isnull=False,
        ).update(closed=timezone.now())

    def run(self):
        self.cancel_all_followings()
        self.repair_db()
