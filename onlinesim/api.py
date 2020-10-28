import time

import requests
from django.conf import settings
from django.utils import timezone

from onlinesim.exceptions import NoSmsCode

api_key = settings.ONLINESIM_API
base_url = f"https://onlinesim.ru/api/%s.php"
service = 'instagram'

RESPONSE_OK = 1
RESPONSE_NO_NUMBER = 'NO_NUMBER'

SLEEP_TIME = 10


class CountryCodes:
    Russia = 7
    Ukraine = 380
    GreatBritain = 44
    Germany = 49
    all = (
        Russia,
        Ukraine,
        Germany,
        GreatBritain,
    )


def get_numbers_stat(country_code):
    method = 'getNumbersStats'
    url = base_url % method
    return requests.post(url, params=dict(
        apikey=api_key,
        country=country_code

    )).json()


def get_num(country_code, service):
    method = 'getNum'
    url = base_url % method
    return requests.post(url, params=dict(
        apikey=api_key,
        service=service,
        country=country_code
    )).json()


def get_state(tzid, message_to_code=1):
    method = 'getState'
    url = base_url % method
    return requests.post(url, params=dict(
        apikey=api_key,
        tzid=tzid,
        message_to_code=message_to_code,
    )).json()


def get_tzid_phone(owner_username=None):
    from database.models import SimonlineTransaction
    sleep_time = 5
    for country in CountryCodes.all:
        available_cnt = get_numbers_stat(country)['services'][service]['count']
        if available_cnt != 0:
            get_num_response = get_num(country, service)
            time.sleep(sleep_time)
            if get_num_response['response'] != RESPONSE_OK:
                continue
            tzid = get_num_response['tzid']
            phone = get_state(tzid)[0]['number']
            SimonlineTransaction(
                tzid=tzid,
                country_code=country,
                phone=phone,
                owner_username=owner_username
            ).save()
            return tzid, phone
        time.sleep(sleep_time)
    raise RuntimeError("No available phones in simonline")


def get_sms(tzid):
    from database.models import SimonlineTransaction
    simonline_transactions = SimonlineTransaction.objects.get(tzid=tzid)
    attempts = simonline_transactions.getting_attempts
    max_attemtps = attempts + 60
    while True:
        attempts += 1
        try:
            time.sleep(SLEEP_TIME)
            msg = get_state(tzid)[0].get('msg')
            simonline_transactions.getting_attempts = attempts
            if msg:
                simonline_transactions.sms_code = msg
                simonline_transactions.sms_code_timestamp = timezone.now()
                simonline_transactions.success = True
                return msg
            else:
                if attempts >= max_attemtps:
                    simonline_transactions.success = False
                    raise NoSmsCode("Didn't get code")
        finally:
            simonline_transactions.save()


def set_operation_ok(tzid):
    from database.models import SimonlineTransaction
    method = 'setOperationOk'
    url = base_url % method
    response = requests.post(url, params=dict(
        apikey=api_key,
        tzid=tzid,
    )).json()
    simonline_transactions = SimonlineTransaction.objects.get(tzid=tzid)
    simonline_transactions.confirmed_timestamp = timezone.now()
    simonline_transactions.save()
    return response


def get_balance():
    method = 'getBalance'
    url = base_url % method
    return requests.post(url, params=dict(
        apikey=api_key,
    )).json()
