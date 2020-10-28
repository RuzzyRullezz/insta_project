import datetime

import requests

from django.db.models import Count
from django.db import transaction

from database.models import Proxy, Accounts, ExternalProxy
from utils.system_common import is_port_open

min_port = 14000
max_port = 15000


from .get_proxy import get_proxy_list


def get_external_ip():
    get_ip_url = 'http://icanhazip.com/'
    response = requests.get(get_ip_url, timeout=10)
    external_ip = response.text.strip()
    return external_ip


squid_host = get_external_ip()


@transaction.atomic
def remove_all_proxies():
    Proxy.objects.all().delete()


@transaction.atomic
def refresh_external_proxies():
    active_value = '1'
    for proxy in get_proxy_list():
        proxy_data = {
            'uid': proxy['id'],
        }
        proxy_defaults = {
            'host': proxy['host'],
            'port': int(proxy['port']),
            'username': proxy['user'],
            'password': proxy['pass'],
            'ip': proxy['ip'],
            'country': proxy['country'],
            'active': proxy['active'] == active_value,
            'ended': datetime.datetime.fromtimestamp(proxy['unixtime_end'])
        }
        ExternalProxy.objects.update_or_create(**proxy_data, defaults=proxy_defaults)


def get_next_port():
    ports = range(min_port, max_port + 1)
    for port in ports:
        if not is_port_open(port):
            continue
        if Proxy.objects.filter(ip=squid_host, port=port).exists():
            continue
        yield port
    raise RuntimeError("Unreachable statement")


@transaction.atomic
def generate_proxies_for_external():
    port_gen = get_next_port()
    for external_proxy in ExternalProxy.objects.filter(active=True, proxy__isnull=True):
        port = next(port_gen)
        proxy = Proxy.objects.create(
            ip=squid_host,
            port=port,
            enable=True,
        )
        external_proxy.proxy = proxy
        external_proxy.save()


@transaction.atomic
def set_proxies():
    for proxy_account in Accounts.objects.filter(banned=False, proxy__isnull=True):
        next_proxy = Proxy.objects.annotate(
            accounts_cnt=Count(
                'accounts',
            )
        ).order_by('accounts_cnt').first()
        if next_proxy:
            proxy_account.proxy = next_proxy
            proxy_account.save()
