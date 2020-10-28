import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promo_bots.media import upload_for_promo
from database.models import Accounts
from bots.arguments import get_username


if __name__ == '__main__':
    upload_for_promo(Accounts.objects.get(username=get_username()))
