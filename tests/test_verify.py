import bootstrap
bootstrap.setup()

from database.models import Accounts

from promo_bots.browser import verify


def run():
    account = Accounts.objects.get(username='sova_timofei')
    verify(account)


if __name__ == '__main__':
    run()
