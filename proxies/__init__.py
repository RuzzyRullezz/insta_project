import requests

from database.models import Proxy


get_ip_url = 'http://icanhazip.com/'


def get_proxy_dict(proxy):
    if proxy is None:
        return None
    if proxy.username and proxy.password:
        uri = f'{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}'
    else:
        uri = f'{proxy.ip}:{proxy.port}'
    return dict(
        http=f'http://{uri}',
        https=f'https://{uri}',
    )


def check_proxy(proxy):
    proxies = get_proxy_dict(proxy)
    print(f"Checking: {proxies}")
    response = requests.get(get_ip_url, proxies=proxies, timeout=10)
    print(f'Response: {response.text}\n')


def check_all():
    proxies = Proxy.objects.filter(enable=True)
    for proxy in proxies:
        check_proxy(proxy)
