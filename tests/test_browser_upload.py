import os

import bootstrap
bootstrap.setup()

from database.models import Accounts
from promo_bots.browser import PhotoUploader

if __name__ == '__main__':
    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'photo_2.jpg'))
    account = Accounts.objects.get(username='sova_timofei')
    uploader = PhotoUploader(
        account.username,
        account.password,
        account.fb_email,
        account.fb_pass,
        proxy_ip=account.proxy.ip,
        proxy_port=account.proxy.port
    )
    try:
        uploader.login()
        uploader.upload(image_path)
    finally:
        del uploader
