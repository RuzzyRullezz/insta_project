import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promo_bots.profiles import fill_bots


if __name__ == '__main__':
    fill_bots()
