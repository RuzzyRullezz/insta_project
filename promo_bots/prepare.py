import logging

from database.models import Accounts
from promo_bots.media import delete_all_media, upload_for_promo, set_comments, tag_user
from proxies.prepare import set_proxies


def prepare_bot(account: Accounts, force_proxy=None):
    delete_all_media(account)
    upload_for_promo(account, force_proxy=force_proxy)
    set_comments(account)
    tag_user(account)
    set_proxies()
    tg_logger = logging.getLogger('telegram_logger')
    tg_logger.info(f"Account {account.username} is ready. Start promo!")
