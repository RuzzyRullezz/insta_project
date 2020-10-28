import bootstrap
bootstrap.setup()

from database.models import Accounts


def run():
    account = Accounts.objects.get(username='sova_timofei')
    client = account.get_bot_client()
    client.login()
    client.story_look(417100715)


if __name__ == '__main__':
    run()
