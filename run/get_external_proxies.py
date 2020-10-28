import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from proxies.prepare import refresh_external_proxies, generate_proxies_for_external, remove_all_proxies, set_proxies


if __name__ == '__main__':
    refresh_external_proxies()
    remove_all_proxies()
    generate_proxies_for_external()
    set_proxies()
