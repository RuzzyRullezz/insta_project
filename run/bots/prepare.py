import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from bots.arguments import get_username
from promo_bots.prepare import prepare_bot


if __name__ == '__main__':
    prepare_bot(Accounts.objects.get(username=get_username()))
