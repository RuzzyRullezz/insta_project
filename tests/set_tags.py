import bootstrap
bootstrap.setup()

from database.models import Accounts
from promo_bots.media import tag_user


if __name__ == '__main__':
    accounts = [
        'sova_prohor',
        'sova_rustam',
    ]
    for account in accounts:
        tag_user(Accounts.objects.get(username=account))
