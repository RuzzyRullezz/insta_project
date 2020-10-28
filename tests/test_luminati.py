import bootstrap
bootstrap.setup()

from database.models import Accounts


def run():
    account = Accounts.objects.get(username='sova_timofei')
    ig_client = account.get_bot_client()
    ig_client.login()
    ig_client.follow(417100715)
    ig_client.unfollow(417100715)


if __name__ == '__main__':
    run()
