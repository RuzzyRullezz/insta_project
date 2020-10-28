import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from django.db import transaction

from pyctogram.instagram_client.exceptions import InstagramNot2XX

from database.models import Accounts, Profile, Posted, TextContent

if __name__ == '__main__':
    with transaction.atomic():
        for account in Accounts.objects.filter(banned=False):
            try:
                account.get_bot_client().login()
            except InstagramNot2XX as exc:
                if 'inactive user' in exc.msg:
                    print(f"{account.username} - banned!")
                    account.banned = True
                    account.proxy = None
                    account.save()
                    print(f"{account.username}: set banned = True")
                    print(f"{account.username}: set proxy = None")
                    updated_cnt = Profile.objects.filter(owner=account, passed=False).update(owner=None)
                    print(f"{account.username}: clean {updated_cnt} profiles")
                    deleted_cnt, _ = Posted.objects.filter(account=account).delete()
                    print(f"{account.username}: delete {deleted_cnt} posts")
                else:
                    raise
