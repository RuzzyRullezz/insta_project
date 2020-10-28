import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from promoting.process_killer import kill_frozen


if __name__ == '__main__':
    kill_frozen()
