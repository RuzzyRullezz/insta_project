import bootstrap
bootstrap.setup()

from telegram_informer.bot import TgApprover


if __name__ == '__main__':
    TgApprover.run()
