import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from bots.arguments import get_username
from promo_bots.media import tag_user


if __name__ == '__main__':
    tag_user(Accounts.objects.get(username=get_username()))
