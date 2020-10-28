import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promo_bots.cleaner import clear_all_followings


if __name__ == '__main__':
    clear_all_followings()
