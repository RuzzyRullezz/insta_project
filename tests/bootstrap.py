import os
import sys
import logging

import django


def set_exceptcook():
    _default_exceptcook = sys.excepthook

    def excepthook(exctype, value, traceback):
        if isinstance(value, KeyboardInterrupt):
            _default_exceptcook(exctype, value, traceback)
        else:
            logging.getLogger().exception('', exc_info=(exctype, value, traceback))

    sys.excepthook = excepthook


def setup():
    django_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.append(django_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insta_project.settings")
    django.setup()
    set_exceptcook()
