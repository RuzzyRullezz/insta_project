import decimal
import logging

import bootstrap
bootstrap.setup()

from onlinesim.api import get_balance

tg_logger = logging.getLogger('telegram_logger')


BALANCE_LIMIT = 100


def run():
    balance = decimal.Decimal(get_balance()['balance'])
    if balance <= BALANCE_LIMIT:
        tg_logger.info(f'SIMONLINE low balance: {balance}')


if __name__ == '__main__':
    run()
