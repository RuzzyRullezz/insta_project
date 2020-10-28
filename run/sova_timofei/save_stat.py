import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from promoting.saver import save_stat
from sova_timofei import username


def run():
    save_stat(Accounts.objects.get(username=username))


if __name__ == '__main__':
    run()
