import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import SourceProfile
from profiles_getters.followers_getters import parse_target


def get_username():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Target username", type=str)
    return parser.parse_args().username


if __name__ == '__main__':
    target_username = get_username()
    target = SourceProfile.objects.get(username=target_username)
    parse_target(target, skip=False)

