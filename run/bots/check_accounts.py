import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promo_bots.create_bot import check_accounts


def get_filepath():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="File path", type=str)
    return parser.parse_args().filepath


def run():
    filepath = get_filepath()
    check_accounts(filepath)


if __name__ == '__main__':
    run()

