import datetime

import bootstrap
bootstrap.setup()


from promoting.counter_cleaner import CounterCleaner

CounterCleaner(save_period=datetime.timedelta(hours=1)).clean()

