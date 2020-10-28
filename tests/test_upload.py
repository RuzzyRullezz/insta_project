import os

import bootstrap
bootstrap.setup()

from database.models import Accounts


if __name__ == '__main__':
    image_path = os.path.join(os.path.dirname(__file__), 'data', 'photo_1.jpg')
    account = Accounts.objects.get(username='sova_timofei')
    insta_client = account.get_bot_client()
    insta_client.login()
    response = insta_client.client.upload_photo(image_path)
