import psutil
import datetime

delta = datetime.timedelta(hours=1)


def process_killer_predicate(p):
    return 'chrome' in (p.info['name'] or '')\
           and (datetime.datetime.now() - datetime.datetime.fromtimestamp(p.info['create_time']) >= delta)


for proc in filter(process_killer_predicate, psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'create_time'])):
    proc.kill()
    print(f'Killed: {proc.pid} {proc.name()} {proc.cmdline()}')
