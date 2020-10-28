import datetime

import pytz

import bootstrap
bootstrap.setup()

from database.models import Accounts, MediaComments, MediaLiker
from pyctogram.instagram_client.web import get_instagram_id


def run():
    account = Accounts.objects.get(username='sova_timofei')
    client = account.get_bot_client()
    client.login()
    target_id = get_instagram_id('blue_birdy')
    feed_gen = client.client.get_user_feed(target_id)
    for feed in feed_gen:
        likers = client.client.get_media_likers(feed['id'])
        comments = client.client.get_direct_media_comments(feed['id'])
        for liker in likers['users']:
            MediaLiker.objects.update_or_create(
                user_ig_id=liker['pk'],
                media_ig_id=feed['id'],
                defaults=dict(
                    user_username=liker['username'],
                    user_full_name=liker['full_name'],
                    user_is_private=liker['is_private'],
                    user_profile_pic_url=liker['profile_pic_url'],
                    media_code=feed['code'],
                    media_taken_at=datetime.datetime.fromtimestamp(feed['taken_at'], tz=pytz.UTC),
                    media_caption=(feed.get('caption') or {'text': None})['text'],
                )
            )
            print(f'Saved liker: {feed["code"]} - {liker["username"]}')
        for comment in comments['comments']:
            MediaComments.objects.update_or_create(
                ig_id=comment['pk'],
                defaults=dict(
                    text=comment['text'],
                    created_at=datetime.datetime.fromtimestamp(comment['created_at'], tz=pytz.UTC),
                    like_count=comment.get('comment_like_count', 0),
                    user_ig_id=comment['user']['pk'],
                    user_username=comment['user']['username'],
                    user_full_name=comment['user']['full_name'],
                    user_is_private=comment['user']['is_private'],
                    user_profile_pic_url=comment['user']['profile_pic_url'],
                    media_ig_id=feed['id'],
                    media_code=feed['code'],
                    media_taken_at=datetime.datetime.fromtimestamp(feed['taken_at'], tz=pytz.UTC),
                    media_caption=(feed.get('caption') or {'text': None})['text'],
                )
            )
            print(f'Saved comment: {feed["code"]} - {comment["user"]["username"]} - {comment["text"]}')


if __name__ == '__main__':
    run()


