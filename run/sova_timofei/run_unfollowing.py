import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from promoting.promo_unfollowing import UnfollowingPromo
from sova_timofei import username


def run():
    UnfollowingPromo(Accounts.objects.get(username=username)).run()


if __name__ == '__main__':
    run()
