import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import bootstrap
bootstrap.setup()

from promo_bots.media import upload_single


if __name__ == '__main__':
    upload_single()
