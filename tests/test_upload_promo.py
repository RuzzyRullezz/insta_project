import bootstrap
bootstrap.setup()

from promo_bots.media import upload_for_promo

from database.models import Accounts


if __name__ == '__main__':
    account = Accounts.objects.get(username='sova_rustam')
    upload_for_promo(account)
