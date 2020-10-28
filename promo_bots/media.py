import os
import pickle
import time
import random

from database.models import Accounts, TextContent
from pyctogram.instagram_client.client import InstagramClient, InstagramNot2XX
from pyctogram.instagram_client.web import get_user_info

from painter.sova_timofei import SovaTimofeiPainter
from proxies import get_proxy_dict

max_uploads = 12
tagged_count = 6
base_profile_username = 'sova_timofei'
media_folder = '/tmp'
sleep_time = 30
sleep_before_tag = 30
caption = 'Больше юмора в основном профиле - @sova_timofei'


def get_target_media(client, target_id):
    cached_file = os.path.join('/tmp/', f'media_{target_id}.dat')
    if os.path.exists(cached_file):
        with open(cached_file, 'rb') as rf:
            media_list = pickle.load(rf)
            return media_list
    else:
        media_list = list(client.get_user_feed(target_id))
        with open(cached_file, 'wb') as wf:
            pickle.dump(media_list, wf)
        return media_list


def delete_all_media(account: Accounts):
    bot_client = account.get_bot_client()
    bot_client.login()
    user_id = int(get_user_info(account.username)['pk'])
    for feed in bot_client.client.get_user_feed(user_id):
        bot_client.client.delete_media(feed['id'])


def upload_for_promo(account: Accounts, force_proxy=None):
    client = account.get_bot_client()
    if force_proxy:
        client.client.session.proxies = force_proxy
    client.login()
    for i in range(max_uploads):
        text_content = TextContent.objects.filter(
            ignore=False,
            instagram_post__isnull=True
        ).order_by('added').first()
        if text_content is None:
            raise RuntimeError("No media for bot upload")
        text_content.owner = account
        text_content.save()
        ig_post_id = text_content.upload(client, SovaTimofeiPainter())
        if ig_post_id is None:
            continue
        print(f"Upload post id = {ig_post_id}")
        time.sleep(sleep_time)


def upload_single():
    sova_timofei_ig_id = int(get_user_info(base_profile_username)['pk'])
    for account in Accounts.objects.filter(banned=False).exclude(username=base_profile_username):
        fullname = get_user_info(account.username)['full_name']
        media_caption = caption + f'- {fullname} рекомендует!'
        client = InstagramClient(account.username, account.password, proxies=get_proxy_dict(account.proxy))
        client.login()
        text_content = TextContent.objects.filter(
            ignore=False,
            instagram_post__isnull=True
        ).order_by('added').first()
        if text_content is None:
            raise RuntimeError("No media for bot upload")
        ig_post_id = text_content.upload(client, SovaTimofeiPainter(), caption=media_caption)
        if ig_post_id is None:
            continue
        print(f"Uploaded for {account.username}")
        try:
            time.sleep(sleep_before_tag)
            place = (random.randint(3000000, 7000000) / 10000000, random.randint(3000000, 7000000) / 10000000)
            client.tag_user(ig_post_id, sova_timofei_ig_id, place, caption=media_caption)
            print(f"Set tag for {account.username}")
        except InstagramNot2XX:
            pass


def set_comments(account):
    sova_bot_client = Accounts.objects.get(username=base_profile_username).get_bot_client()
    sova_bot_client.login()
    for media in list(sova_bot_client.client.get_user_feed(int(get_user_info(account.username)['pk'])))[:3]:
        sova_bot_client.client.comment(media['id'], 'Бoльше отборного юмора у меня на странице')
        time.sleep(30)


def tag_user(account):
    bot_client = account.get_bot_client()
    bot_client.login()
    for media in list(bot_client.client.get_user_feed(int(get_user_info(account.username)['pk'])))[:3]:
        place = (random.randint(3000000, 7000000) / 10000000, random.randint(3000000, 7000000) / 10000000)
        bot_client.tag_user(media['id'], int(get_user_info(base_profile_username)['pk']), position=place)
        time.sleep(30)
