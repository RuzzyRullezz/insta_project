import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from upload_selector.approve_sender import ApproveSender
from sova_timofei import username


def run():
    ApproveSender(username).send()


if __name__ == '__main__':
    run()
