import bootstrap
bootstrap.setup()

from database.models import Accounts
from pyctogram.instagram_client.web import get_instagram_id


def run():
    account = Accounts.objects.get(username='sova_timofei')
    client = account.get_bot_client()
    client.login()
    target_id = get_instagram_id('blue_birdy')
    feed_gen = client.client.get_user_feed(target_id)
    for feed in feed_gen:
        print(feed)



if __name__ == '__main__':
    run()


