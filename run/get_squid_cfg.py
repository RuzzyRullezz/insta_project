import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from proxies.get_proxy import get_squid_conf


if __name__ == '__main__':
    print(get_squid_conf())
