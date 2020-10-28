import time

import bootstrap
bootstrap.setup()

from django_pglocks import advisory_lock


if __name__ == '__main__':
    with advisory_lock(1, wait=False) as acquired:
        time.sleep(60)
