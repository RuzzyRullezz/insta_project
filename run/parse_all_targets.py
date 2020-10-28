import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from profiles_getters.followers_getters import parse_all_targets


if __name__ == '__main__':
    parse_all_targets()
