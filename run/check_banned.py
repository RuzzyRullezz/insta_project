import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from pyctogram.instagram_client.client import InstagramClient
from pyctogram.instagram_client import exceptions

from database.models import Accounts

if __name__ == '__main__':
    for account in Accounts.objects.all().order_by('id'):
        pure_client = InstagramClient(account.username, account.password, proxies=
                                      {'http': 'http://80.241.219.59:14035', 'https': 'https://80.241.219.59:14035'})
        try:
            pure_client.login()
            if account.banned:
                print(f'{account.id} {account.username} - WRONG BANNED')
        except (exceptions.InstagramChallengeRequired, exceptions.InstagramCheckpointRequired):
            pass
        except exceptions.InstagramAccountHasBeenDisabled:
            print(f"{account.id} {account.username} - BANNED ({account.banned})")
        except exceptions.InstagramConsentRequired:
            print(f"{account.id} {account.username} - CONSENT ({account.banned})")
