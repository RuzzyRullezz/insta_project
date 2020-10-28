import bootstrap
bootstrap.setup()

from pyctogram.instagram_client.web import get_instagram_id
from database.models import Accounts


def run():
    account = Accounts.objects.get(username='sova_timofei')
    target_id = get_instagram_id('blue_birdy')
    client = account.get_bot_client()
    client.login()
    story_reel = client.get_user_story_feed(target_id)['reel']
    if story_reel:
        response = client.mark_media_seen(story_reel['items'])
        print(response)


if __name__ == '__main__':
    run()
