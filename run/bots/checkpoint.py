import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from bots.arguments import get_username
from promo_bots.browser import verify


if __name__ == '__main__':
    verify(Accounts.objects.get(username=get_username()))

