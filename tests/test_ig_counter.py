import datetime
import time

import bootstrap
bootstrap.setup()

from counters.redis_counter import TimeCounter


def run():
    sova_platon_counter = TimeCounter("sova_platon:following", period=datetime.timedelta(seconds=30))
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    sova_platon_counter.inc()
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(1)
    print(sova_platon_counter.count())
    time.sleep(30)
    print(sova_platon_counter.count())

if __name__ == '__main__':
    run()