import multiprocessing

import bootstrap
bootstrap.setup()

from database.async_saver import DBSaver


def run_db_saver():
    DBSaver().run()


if __name__ == '__main__':
    consumers_count = 20
    consumers_list = []

    for i in range(consumers_count):
        p = multiprocessing.Process(target=run_db_saver)
        consumers_list.append(p)
        p.start()
