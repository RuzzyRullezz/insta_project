from pyctogram.instagram_client.web import get_user_info
from database.models import Accounts, IgStat


def save_stat(account: Accounts):
    user_info = get_user_info(account.username, proxy=None)
    if user_info:
        IgStat.objects.create(
            account=account,
            followers_count=user_info['follower_count'],
            following_count=user_info['following_count'],
        )
