import bootstrap
bootstrap.setup()

from onlinesim.api import get_balance


def run():
    print(get_balance())


if __name__ == '__main__':
    run()
