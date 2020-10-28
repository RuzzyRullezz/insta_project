import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from proxies.check import check_external_proxies


if __name__ == '__main__':
    check_external_proxies()
