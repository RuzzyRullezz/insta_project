import bootstrap
bootstrap.setup()

from imap_client.get_mail import get_verify_link


def run():
    get_verify_link('sova_varlam@ruzzy.pro', 'asdjasjdhja')


if __name__ == '__main__':
    run()
