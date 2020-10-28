import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promo_bots.create_bot import generate_account


def get_credentials():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Old username", type=str)
    parser.add_argument("password", help="Old password", type=str)
    args = parser.parse_args()
    return args.username, args.password


def run():
    old_username, old_password = get_credentials()
    generate_account(old_username, old_password)


if __name__ == '__main__':
    run()

