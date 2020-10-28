import os
import sys
import logging

import django

non_loggable_exc_classes = []


def register_non_loggable_exceptions():
    from pyctogram.instagram_client.exceptions import InstagramDidntChangeTheStatus
    from promoting.exceptions import IgLimitReachedException, ConditionWaitException
    from pyctogram.instagram_client.exceptions import InstagramUserRestricred, InstagramSpamDetected
    from promo_bots.exceptions import WaitError
    from requests.exceptions import ChunkedEncodingError
    from imap_client.exceptions import NoNewEmails
    from onlinesim.exceptions import NoSmsCode

    non_loggable_exc_classes.extend([
        KeyboardInterrupt,
        ConditionWaitException,
        InstagramDidntChangeTheStatus,
        IgLimitReachedException,
        InstagramUserRestricred,
        InstagramSpamDetected,
        WaitError,
        ChunkedEncodingError,
        NoNewEmails,
        NoSmsCode,
    ])


def set_exceptcook():
    _default_exceptcook = sys.excepthook

    def excepthook(exctype, value, traceback):
        if isinstance(value, tuple(non_loggable_exc_classes)):
            _default_exceptcook(exctype, value, traceback)
        else:
            logging.getLogger().exception('', exc_info=(exctype, value, traceback))

    sys.excepthook = excepthook


def setup(set_cook=True):
    django_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.append(django_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insta_project.settings")
    django.setup()
    if set_cook:
        register_non_loggable_exceptions()
        set_exceptcook()
