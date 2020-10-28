import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from database.models import Accounts
from consumers.uploader import InstagramUploader

from sova_timofei import username


def run():
    account = Accounts.objects.get(username=username)
    InstagramUploader(account).run()


if __name__ == '__main__':
    run()
