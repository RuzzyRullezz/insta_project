import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from pyctogram.instagram_client.web import get_user_info

from database.models import SourceProfile


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Source profile username", type=str)
    return parser.parse_args()


def run():
    username = get_arguments().username
    info = get_user_info(username)
    if info is None:
        print(f"Can't find account with username = {username}")
    source_profile = SourceProfile.objects.filter(instagram_id=info['pk']).first()
    if source_profile is None:
        source_profile = SourceProfile(instagram_id=info['pk'])
    source_profile.username = info['username']
    source_profile.save()


if __name__ == '__main__':
    run()

