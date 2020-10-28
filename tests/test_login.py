import bootstrap
bootstrap.setup()

from database.models import Accounts


def run():
    account = Accounts.objects.get(username='sova__boris')
    client = account.get_bot_client()
    client.login(force=True)


if __name__ == '__main__':
    run()
