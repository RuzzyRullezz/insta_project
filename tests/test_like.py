import bootstrap
bootstrap.setup()

from pyctogram.instagram_client.web import get_instagram_id
from database.models import Accounts


def run():
    account = Accounts.objects.get(username='sova_timofei')
    target_id = get_instagram_id('blue_birdy')
    client = account.get_bot_client()
    client.login()
    last_media = client.get_last_media_id(target_id)
    if last_media:
        response = client.like(last_media['id'])
        print(response)


if __name__ == '__main__':
    run()
