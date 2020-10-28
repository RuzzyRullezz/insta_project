import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()


from database.models import Accounts
from promo_bots.media import delete_all_media
from bots.arguments import get_username


if __name__ == '__main__':
    delete_all_media(Accounts.objects.get(username=get_username()))

