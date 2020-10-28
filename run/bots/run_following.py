import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from promoting.promo_following import FollowingPromo

from bots.arguments import get_username


def run():
    username = get_username()
    account = Accounts.objects.get(username=username)
    FollowingPromo(account).run()


if __name__ == '__main__':
    run()
