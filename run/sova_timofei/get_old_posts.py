import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from pyctogram.instagram_client.web import get_instagram_id

from database.models import Accounts, OldPost
from sova_timofei import username


def run():
    parser_account = Accounts.objects.get(username='sova_ignat')
    sova_timofei_account = Accounts.objects.get(username=username)
    client = parser_account.get_bot_client()
    client.login()
    target_id = get_instagram_id(username)
    feeds = client.client.get_user_feed(int(target_id))
    for feed in feeds:
        obj, created = OldPost.objects.update_or_create(
            ig_id=feed['id'],
            defaults=dict(
                taken_at=feed['taken_at'],
                owner=sova_timofei_account,
                media_type=feed['media_type'],
                code=feed['code'],
                comment_count=feed.get('comment_count', 0),
                like_count=feed['like_count'],
                url=feed.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
            )
        )
        if created:
            print(f'Saved post with url = {obj.url} and id = {obj.ig_id}')
        else:
            print(f'Updated post with url = {obj.url} and id = {obj.ig_id}')

if __name__ == '__main__':
    run()
