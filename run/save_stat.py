import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup(set_cook=False)

from database.models import Accounts
from promoting.saver import save_stat


def run():
    for account in Accounts.objects.all():
        save_stat(account)
        time.sleep(10)


if __name__ == '__main__':
    run()
