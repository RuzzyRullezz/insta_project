import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from bots.arguments import get_username
from promo_bots.profiles import get_new_promo_profiles


if __name__ == '__main__':
    get_new_promo_profiles(Accounts.objects.get(username=get_username()))

