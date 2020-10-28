import bootstrap
bootstrap.setup()

from pyctogram.instagram_client import client

from database.models import Profile


def save_profile():
    cl = client.InstagramClient('', '')
    cl.login()
    info = cl.get_user_info(295116275)['user']
    info['ipk'] = info.pop('pk')
    info['hd_profile_pic_url_info'] = info.pop('hd_profile_pic_url_info', {'url': ''})['url']
    info.pop('hd_profile_pic_versions')
    Profile.objects.create(**info)


if __name__ == '__main__':
    save_profile()
