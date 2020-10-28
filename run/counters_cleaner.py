import bootstrap
bootstrap.setup()

from promoting.counter_cleaner import CounterCleaner


if __name__ == '__main__':
    CounterCleaner().clean()
