import bootstrap
bootstrap.setup()

from database.models import Proxy
from proxies import check_proxy


def run():
    for proxy in Proxy.objects.filter(enable=True):
        check_proxy(proxy)


if __name__ == '__main__':
    run()
