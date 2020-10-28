import json
import os
import traceback
import functools
import logging
from abc import ABCMeta, abstractmethod

import pytz
from django.db import transaction
from django.utils import timezone
from mq_consumer.checkers import MQChecker
from mq_consumer.consumers import NotEmptyConsumer
from pyctogram.instagram_client.exceptions import InstagramAccountHasBeenDisabled

from database.models import Accounts, PromoHistory, PromoType
from utils.mq import get_connector


tg_logger = logging.getLogger('telegram_logger')


class Promotion(metaclass=ABCMeta):
    lock_file_pattern = '/tmp/promo_%d.lock'
    timezone = pytz.timezone('Europe/Moscow')
    promo_type = NotImplemented
    sleep_time = NotImplemented
    max_parallel_proxy_workers = 2

    class PromoConsumer(NotEmptyConsumer):
        def __init__(self, queue_name, promo_obj_handler):
            self.promo_obj_handler = promo_obj_handler
            super().__init__(get_connector(queue_name), self.message_handle)

        def message_handle(self, channel, method, properties, body):
            promo_obj_json = json.loads(body)
            self.promo_obj_handler(promo_obj_json)
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def __init__(self, account: Accounts):
        self.account = account
        self.ig_client = self.account.get_bot_client()
        self.ig_client_logged_in = False
        promo_type_str = PromoType.get_verbose(self.promo_type)
        queue_name = f'{account.username}_{promo_type_str}'
        promo_obj_handler = self.check_banned_decorator(self.process_promo_obj)
        self.mq_consumer = self.PromoConsumer(queue_name, promo_obj_handler)

    @abstractmethod
    def process_promo_obj(self, promo_obj_json):
        pass

    @abstractmethod
    def prepare_promo_objs(self, publisher):
        pass

    def pre_run(self):
        pass

    def get_message_count(self):
        return MQChecker(self.mq_consumer.connector, passive=False, durable=True).get_message_count()

    def obtains_messages(self):
        process_data_cnt = self.get_message_count()
        if process_data_cnt == 0:
            publisher = self.mq_consumer.get_json_publisher()
            self.prepare_promo_objs(publisher)

    def check_banned_decorator(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except InstagramAccountHasBeenDisabled:
                self.account.banned = True
                self.account.save()
                tg_logger.info(f"Account {self.account.username} has been disabled!")
                raise
        return wrapper

    def run(self):
        with transaction.atomic():
            list(Accounts.objects.filter(proxy=self.account.proxy).select_for_update())
            if PromoHistory.objects.filter(
                account=self.account,
                end__isnull=True,
            ).exists():
                return
            if PromoHistory.objects.filter(
                account__proxy=self.account.proxy,
                end__isnull=True,
            ).count() >= self.max_parallel_proxy_workers:
                return
            history = PromoHistory.objects.create(
                promo_type=self.promo_type,
                account=self.account,
                process_id=os.getpid(),
            )
        try:
            self.pre_run()
            self.obtains_messages()
            self.mq_consumer.start_consuming()
        except BaseException:
            history.traceback = traceback.format_exc()
            history.success = False
            raise
        else:
            history.success = True
        finally:
            history.end = timezone.now()
            history.save()
