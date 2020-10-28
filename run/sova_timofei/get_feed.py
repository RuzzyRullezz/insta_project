import shutil
import sys
import os
import random

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from pyctogram.instagram_client.client import InstagramClient
from pyctogram.instagram_client.web import get_user_info

from sova_timofei import username


save_folder = os.path.join(os.path.dirname(__file__), os.path.pardir, 'data', 'upload_images')


def run():
    if os.path.isdir(save_folder):
        shutil.rmtree(save_folder, ignore_errors=False, onerror=None)
    os.mkdir(save_folder)
    account = Accounts.objects.get(username=username)
    user_id = get_user_info('sova_timofei')['pk']
    client = InstagramClient(account.username, account.password)
    client.login()
    feeds = sorted(client.get_user_feed(int(user_id)), key=lambda f: f['like_count'], reverse=True)
    for feed in random.sample(feeds, k=12):
        print(f"{feed['like_count']}: {feed['image_versions2']['candidates'][0]['url']}")
        with open(os.path.join(save_folder, f'{feed["like_count"]}_{feed["pk"]}.jpg'), 'wb') as wf:
            wf.write(requests.get(feed['image_versions2']['candidates'][0]['url']).content)


if __name__ == '__main__':
    run()
