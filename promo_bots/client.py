import itertools
import time
from json import JSONDecodeError
from typing import List

import requests
from django.utils.timezone import make_aware
from pyctogram.instagram_client.client import InstagramClient, InstagramCheckpointRequired, \
    InstagramChallengeRequired, InstagramAccountHasBeenDisabled, InstagramNotJson, InstagramLoginRequired, Instagram5XX, \
    Instagram404, InstagramConsentRequired
from pyctogram.instagram_client.logger import RequestLog
from pyctogram.instagram_client.urls import FOLLOWERS_URL
from requests.exceptions import ProxyError

from database.models import PromoType, Accounts
from luminati.proxy import get_valid_ig_client
from promo_bots.browser import CheckpointChallenger
from promoting.exceptions import IgLimitReachedException

from .exceptions import NotValidIP

MAX_ATTEMPTS = 100
SLEEP = 5


class IgClient:
    def __init__(self, username, password, email_user, email_password, account_id=None,
                 proxy_ip=None, proxy_port=None, login_cookies=None, log_func=None, keep_old_proxy=True):
        self.username = username
        self.password = password
        self.email_user = email_user
        self.email_password = email_password
        self.account_id = account_id
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.log_func = log_func
        if self.log_func is None:
            self.log_func = self.log_request
        self.login_cookies = login_cookies
        self.client = None
        self.phone = None
        self.keep_old_proxy = keep_old_proxy
        self.client_proxies = self.get_requests_proxies(self.proxy_ip, self.proxy_port)
        self.create_ig_client()

    @staticmethod
    def get_counter(username, promo_type):
        account = Accounts.objects.get(username=username)
        db_counter_cls = PromoType.get_counter_cls(promo_type)
        limit = PromoType.get_limit(promo_type)
        return db_counter_cls(account, limit=limit)

    @staticmethod
    def get_requests_proxies(proxy_ip, proxy_port):
        if proxy_ip and proxy_port:
            uri = f'{proxy_ip}:{proxy_port}'
            return dict(
                http=f'http://{uri}',
                https=f'https://{uri}',
            )
        else:
            return None

    def create_ig_client(self):
        self.client = InstagramClient(
            self.username,
            self.password,
            proxies=self.client_proxies,
            login_cookies=self.login_cookies,
            log_func=self.log_func,
            session_file=f'/tmp/{self.username}_session.dat'
        )

    def create_ig_client_via_luminati(self):
        self.client = get_valid_ig_client(self.username, self.password, log_func=self.log_func)
        if self.keep_old_proxy:
            self.client.session.proxies = self.client_proxies

    def checkpoint_challenger_login(self, force=False):
        max_attempts = MAX_ATTEMPTS
        attempts = 0
        while True:
            try:
                attempts += 1
                if force:
                    self.client.logged_in = False
                self.client.login()
                break
            except (InstagramCheckpointRequired, InstagramChallengeRequired, InstagramLoginRequired):
                if attempts < max_attempts:
                    try:
                        self.login_cookies, self.phone = CheckpointChallenger(
                            self.username,
                            self.password,
                            self.email_user,
                            self.email_password,
                            proxy_ip=self.proxy_ip,
                            proxy_port=self.proxy_port
                        ).challenge()
                        self.create_ig_client()
                    except NotValidIP:
                        self.create_ig_client_via_luminati()
                        return
                else:
                    raise
            except InstagramConsentRequired:
                CheckpointChallenger(
                    self.username,
                    self.password,
                    self.email_user,
                    self.email_password,
                    proxy_ip=self.proxy_ip,
                    proxy_port=self.proxy_port
                ).select_bdate()
            except (requests.exceptions.RequestException, ProxyError, JSONDecodeError, InstagramNotJson, Instagram5XX):
                if attempts <= max_attempts:
                    time.sleep(float(attempts) / 2)
                    continue
                else:
                    raise

    def login(self, force=False):
        self.checkpoint_challenger_login(force=force)

    def call_ig_api(self, api_func, args=None, kwargs=None, counter=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        if counter:
            available_requests_cnt = counter.get_available_requests_count()
            if available_requests_cnt <= 0:
                raise IgLimitReachedException
        request_max_attempts = 100
        attempts = 0
        while True:
            try:
                attempts += 1
                response = api_func(*args, **kwargs)
                if response and counter:
                    counter.inc()
                return response
            except (InstagramChallengeRequired, InstagramCheckpointRequired, InstagramLoginRequired):
                if attempts <= request_max_attempts:
                    self.client.logged_in = False
                    self.login()
                    continue
                else:
                    raise
            except (requests.exceptions.RequestException, ProxyError, JSONDecodeError, InstagramNotJson, Instagram5XX):
                if attempts <= request_max_attempts:
                    time.sleep(float(attempts) / 2)
                    continue
                else:
                    raise
            except Instagram404:
                return None

    def get_relation(self, user_instagram_id):
        return self.call_ig_api(self.client.get_user_friendship, args=(user_instagram_id,))

    def follow(self, user_instagram_id):
        return self.call_ig_api(self.client.follow, args=(user_instagram_id,),
                                counter=self.get_counter(self.username, PromoType.following))

    def unfollow(self, user_instagram_id):
        return self.call_ig_api(self.client.unfollow, args=(user_instagram_id,),
                                counter=self.get_counter(self.username, PromoType.unfollowing))

    def get_user_story_feed(self, user_instagram_id):
        return self.call_ig_api(self.client.get_user_story_feed, args=(user_instagram_id,))

    def mark_media_seen(self, items):
        return self.call_ig_api(self.client.mark_media_seen, args=(items,),
                                counter=self.get_counter(self.username, PromoType.looking))

    def story_look(self, user_instagram_id):
        reel = self.get_user_story_feed(user_instagram_id)['reel']
        if reel is None:
            return None
        items = reel['items']
        return self.mark_media_seen(items)

    def upload_photo(self, photo_path, uid=None, caption=''):
        return self.call_ig_api(self.client.upload_photo, args=(photo_path,), kwargs=dict(uid=uid, caption=caption))

    def tag_user(self, media_id, user_id, position, caption=''):
        return self.call_ig_api(self.client.tag_user, args=(media_id, user_id, position), kwargs=dict(caption=caption))

    def change_profile_picture(self, photo_path):
        return self.call_ig_api(self.client.change_profile_picture, args=(photo_path,))

    def edit_profile(self, username, email, gender,
                     first_name=None, biography=None, external_url=None, phone_number=None):
        return self.call_ig_api(self.client.edit_profile,
                                args=(username, email, gender),
                                kwargs=dict(
                                    first_name=first_name,
                                    biography=biography,
                                    external_url=external_url,
                                    phone_number=phone_number
                                ))

    def send_confirm_email(self):
        return self.call_ig_api(self.client.send_confirm_email)

    def change_password(self, new_password):
        return self.call_ig_api(self.client.change_password, args=(new_password, ))

    def send_sms_code(self, phone):
        return self.call_ig_api(self.client.send_sms_code, args=(phone,))

    def verify_sms_code(self, phone, code):
        return self.call_ig_api(self.client.verify_sms_code, args=(phone, code))

    def like(self, media_id):
        return self.call_ig_api(self.client.like, args=(media_id,))

    def post(self, url, params=None):
        def make_post():
            response = self.client.session.post(url, params=params, headers=self.client.headers)
            return self.client.get_json(response)
        return self.call_ig_api(make_post)

    def get_last_media_id(self, user_id):
        return self.call_ig_api(self.client.get_last_media_id, args=(user_id,))

    def get_session(self):
        return self.client.session

    def log_request(self, log_record: RequestLog):
        from database.models import IgLog
        if self.account_id:
            log_params = log_record.__dict__
            log_params.update({
                'account_id': self.account_id,
                'request_time': make_aware(log_params.pop('request_timestamp')),
                'response_time': log_params.pop('response_timestamp'),
            })
            if log_params['response_time']:
                log_params['response_time'] = make_aware(log_params['response_time'])
            # TODO: убрать костыль
            if isinstance(log_params['request_body'], bytes):
                try:
                    log_params['request_body'] = log_params['request_body'].decode()
                except UnicodeDecodeError:
                    log_params['request_body'] = ''
            if isinstance(log_params['response_body'], bytes):
                try:
                    log_params['response_body'] = log_params['response_body'].decode()
                except UnicodeDecodeError:
                    log_params['response_body'] = ''
            IgLog(**log_params).save_async()


class IgClientSwarm:
    def __init__(self, ig_clients: List[IgClient], target_user_id):
        self.ig_clients = ig_clients
        self.target_user_id = target_user_id

    def parse(self):
        for c in self.ig_clients[::]:
            try:
                c.login()
            except InstagramAccountHasBeenDisabled:
                self.ig_clients.remove(c)
        list(map(lambda c: c.login(), self.ig_clients))
        client_cycle = itertools.cycle(self.ig_clients)
        url = FOLLOWERS_URL % self.target_user_id
        max_id = None
        while True:
            ig_client = next(client_cycle)
            if max_id:
                params = dict(max_id=max_id, big_list='true')
            else:
                params = {}
            response_json = ig_client.post(url, params=params)
            yield response_json['users']
            max_id = response_json.get('next_max_id')
            if max_id is None:
                break
