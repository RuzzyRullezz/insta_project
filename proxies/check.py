import requests

from database.models import ExternalProxy
from proxies import get_proxy_dict

get_ip_url = 'http://icanhazip.com/'


def check_external_proxies():
    for ext_proxy in ExternalProxy.objects.filter(active=True, proxy__isnull=False):
        print(f'\nCheck: {ext_proxy.host}:{ext_proxy.port} -> {ext_proxy.ip}')
        requests_proxies = get_proxy_dict(ext_proxy.proxy)
        response = requests.get(get_ip_url, proxies=requests_proxies, timeout=10)
        result_ip = response.text.strip()
        print(f'Response: {result_ip}')
        print(f'Compare: {result_ip == ext_proxy.ip}')
