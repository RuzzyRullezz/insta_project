import threading

from proxies import get_proxy_dict
from database.models import Accounts
from promoting.followings_cleaner import FollowingsCleaner


def clear_all_followings():
    threads = []
    for account in Accounts.objects.all():
        cleaner = FollowingsCleaner(account, proxies=get_proxy_dict(account.proxy))
        thread = threading.Thread(target=cleaner.run)
        threads.append(thread)
        thread.start()
