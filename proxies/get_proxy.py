import requests

from django.conf import settings

from database.models import ExternalProxy


def get_proxy_list():
    proxies = requests.get(settings.GET_PROXY_URL).json()['list'].values()
    return proxies


def get_squid_conf():
    header = 'acl all src 0.0.0.0/0' \
             '\nhttp_access allow all'
    footer = '\n\nnever_direct allow all' \
             '\nhttp_access deny all'
    proxy_template = '\n\nacl {acl_name} localport {port}' \
                     '\nhttp_port {port}' \
                     '\ncache_peer {external_proxy_host} parent {external_proxy_port} 0 \\' \
                     '\n  no-query \\' \
                     '\n  login={external_proxy_user}:{external_proxy_pass} \\' \
                     '\n  connect-fail-limit=99999999 \\' \
                     '\n  proxy-only \\' \
                     '\n  name={peer_name}' \
                     '\ncache_peer_access {peer_name} allow {acl_name}'
    cfg = header
    for external_proxy in ExternalProxy.objects.filter(proxy__isnull=False, active=True).select_related('proxy'):
        cfg += proxy_template.format(**dict(
            acl_name=f'acl_port_{external_proxy.proxy.port}',
            port=external_proxy.proxy.port,
            external_proxy_host=external_proxy.host,
            external_proxy_port=external_proxy.port,
            external_proxy_user=external_proxy.username,
            external_proxy_pass=external_proxy.password,
            peer_name=f'peer_port_{external_proxy.proxy.port}'
        ))
    cfg += footer
    return cfg
